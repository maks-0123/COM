import type { PositionFix, ScenarioFile } from '../../domain/types'
import type { FixListener, PositionSource, ResetListener, SourceState } from '../PositionSource'
import type { ReplayClock } from './ReplayClock'

// Проигрывание записанного сценария.
//
// Источник берёт отметки из уже провалидированного ScenarioFile (parser
// сортирует их по времени) и выдаёт их по мере того, как часы доходят до
// соответствующего ts. Для карты это неотличимо от живого потока: приходит
// одна отметка за другой.

export type FileReplayOptions = {
	/** Зациклить запись: после последней отметки начать сначала. */
	loop?: boolean
}

export class FileReplaySource implements PositionSource {
	readonly #fixes: PositionFix[]
	readonly #clock: ReplayClock
	readonly #loop: boolean
	readonly #fixListeners = new Set<FixListener>()
	readonly #resetListeners = new Set<ResetListener>()

	#cursor = 0
	#state: SourceState = 'idle'
	#offTick: (() => void) | undefined
	#draining = false

	constructor(scenario: ScenarioFile, clock: ReplayClock, options: FileReplayOptions = {}) {
		// Копия и сортировка: источник не должен зависеть от порядка в файле.
		this.#fixes = [...scenario.fixes].sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts))
		this.#clock = clock
		this.#loop = options.loop ?? false
	}

	get state(): SourceState {
		return this.#state
	}

	start(): void {
		if (this.#state === 'playing') return
		if (this.#fixes.length === 0) {
			this.#state = 'ended'
			return
		}

		this.#cursor = 0
		this.#state = 'playing'
		this.#offTick = this.#clock.onTick((now) => this.#drain(now))
		// Перемотка в начало: первый же тик выдаст отметки с минимальным ts.
		this.#clock.seek(this.#startMs())
		this.#clock.start()
	}

	stop(): void {
		this.#offTick?.()
		this.#offTick = undefined
		this.#clock.pause()
		this.#state = 'idle'
	}

	onFix(listener: FixListener): () => void {
		this.#fixListeners.add(listener)
		return () => {
			this.#fixListeners.delete(listener)
		}
	}

	onReset(listener: ResetListener): () => void {
		this.#resetListeners.add(listener)
		return () => {
			this.#resetListeners.delete(listener)
		}
	}

	#startMs(): number {
		return Date.parse(this.#fixes[0].ts)
	}

	/** Выдаёт все отметки, время которых уже наступило. */
	#drain(now: number): void {
		if (this.#draining) return
		this.#draining = true
		try {
			// Перемотка назад: забываем выданное и начинаем заново.
			if (this.#cursor > 0 && now < Date.parse(this.#fixes[this.#cursor - 1].ts)) {
				this.#cursor = 0
				this.#emitReset()
			}

			while (this.#cursor < this.#fixes.length) {
				const fix = this.#fixes[this.#cursor]
				if (Date.parse(fix.ts) > now) break
				this.#cursor += 1
				for (const listener of this.#fixListeners) listener(fix)
			}

			if (this.#cursor >= this.#fixes.length) this.#finish()
		} finally {
			this.#draining = false
		}
	}

	#finish(): void {
		if (this.#loop) {
			// Сбрасываем позиции и переводим часы в начало записи.
			// Повторная выдача произойдёт на следующем тике.
			this.#cursor = 0
			this.#emitReset()
			this.#clock.seek(this.#startMs())
			return
		}

		this.#clock.pause()
		this.#state = 'ended'
	}

	#emitReset(): void {
		for (const listener of this.#resetListeners) listener()
	}
}
