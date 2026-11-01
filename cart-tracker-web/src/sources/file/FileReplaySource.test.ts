import { describe, expect, it } from 'vitest'
import type { PositionFix, ScenarioFile } from '../../domain/types'
import type { ClockListener, ReplayClock } from './ReplayClock'
import { FileReplaySource } from './FileReplaySource'

// Ручные часы: время двигается только по команде теста, поэтому проверки
// порядка и тайминга занимают миллисекунды, а не реальные секунды записи.

class ManualClock implements ReplayClock {
	#now = 0
	#speed = 1
	#playing = false
	#listeners = new Set<ClockListener>()

	get speed(): number {
		return this.#speed
	}

	get playing(): boolean {
		return this.#playing
	}

	now(): number {
		return this.#now
	}

	start(): void {
		this.#playing = true
	}

	pause(): void {
		this.#playing = false
	}

	seek(nowMs: number): void {
		this.#now = nowMs
		this.#emit()
	}

	setSpeed(speed: number): void {
		this.#speed = speed
	}

	onTick(listener: ClockListener): () => void {
		this.#listeners.add(listener)
		return () => {
			this.#listeners.delete(listener)
		}
	}

	advance(ms: number): void {
		this.#now += ms
		this.#emit()
	}

	#emit(): void {
		for (const listener of this.#listeners) listener(this.#now)
	}
}

const T0 = Date.parse('2026-10-28T09:00:00Z')

function fix(cartId: string, offsetMs: number): PositionFix {
	return {
		cartId,
		ts: new Date(T0 + offsetMs).toISOString(),
		position: { x: offsetMs / 1000, y: 0 },
	}
}

function scenario(fixes: PositionFix[]): ScenarioFile {
	return {
		schemaVersion: 1,
		site: {
			id: 'test',
			name: 'Test',
			coordinateSystem: 'local',
			origin: { lat: 55.9, lon: 37.1 },
			basemap: { type: 'none' },
		},
		stations: [],
		carts: [
			{ id: 'c1', name: 'C1' },
			{ id: 'c2', name: 'C2' },
		],
		fixes,
	}
}

function collect(source: FileReplaySource): string[] {
	const seen: string[] = []
	source.onFix((f) => seen.push(`${f.cartId}@${Date.parse(f.ts) - T0}`))
	return seen
}

describe('FileReplaySource', () => {
	it('на старте выдаёт все отметки с минимальным временем', () => {
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 0), fix('c1', 1000)]), new ManualClock())
		const seen = collect(source)

		source.start()

		expect(seen).toEqual(['c1@0', 'c2@0'])
	})

	it('выдаёт отметки по времени, даже если файл не отсортирован', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 2000), fix('c2', 0), fix('c1', 1000)]), clock)
		const seen = collect(source)

		source.start()
		clock.advance(2000)

		expect(seen).toEqual(['c2@0', 'c1@1000', 'c1@2000'])
	})

	it('не выдаёт одну и ту же отметку дважды', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 500), fix('c1', 1000)]), clock)
		const seen = collect(source)

		source.start()
		clock.advance(100)
		clock.advance(100)
		clock.advance(1000)

		expect(seen).toEqual(['c1@0', 'c2@500', 'c1@1000'])
	})

	it('останавливается на последней отметке и меняет состояние', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 1000)]), clock)
		const seen = collect(source)

		source.start()
		clock.advance(5000)
		const afterEnd = seen.length
		clock.advance(5000)

		expect(source.state).toBe('ended')
		expect(clock.playing).toBe(false)
		expect(seen.length).toBe(afterEnd)
	})

	it('в режиме loop начинает запись заново', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 1000)]), clock, { loop: true })
		const seen = collect(source)
		let resets = 0
		source.onReset(() => {
			resets += 1
		})

		source.start()
		clock.advance(5000)

		expect(source.state).toBe('playing')
		expect(resets).toBe(1)

		clock.advance(0)
		expect(seen.at(-1)).toBe('c1@0')

		clock.advance(1000)
		expect(seen.at(-1)).toBe('c2@1000')
	})

	it('перемотка назад сбрасывает позиции и повторяет выдачу', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 1000)]), clock)
		const seen = collect(source)
		let resets = 0
		source.onReset(() => {
			resets += 1
		})

		source.start()
		clock.advance(5000)
		clock.seek(T0)

		expect(resets).toBe(1)
		expect(seen.at(-1)).toBe('c1@0')
	})

	it('после stop новые отметки не приходят', () => {
		const clock = new ManualClock()
		const source = new FileReplaySource(scenario([fix('c1', 0), fix('c2', 1000)]), clock)
		const seen = collect(source)

		source.start()
		clock.advance(500)
		source.stop()
		clock.advance(5000)

		expect(seen).toEqual(['c1@0'])
		expect(source.state).toBe('idle')
	})
})
