import { describe, expect, it } from 'vitest'
import { createReplayClock } from './ReplayClock'

// Здесь проверяется именно ход реальных часов; логика выдачи отметок
// проверяется отдельно на ручных часах в FileReplaySource.test.ts.

describe('createReplayClock', () => {
	it('идёт со множителем скорости и останавливается по pause', async () => {
		const clock = createReplayClock({ tickMs: 5, speed: 2, startAt: 1000 })

		clock.start()
		await new Promise((resolve) => setTimeout(resolve, 60))
		clock.pause()

		// За 60 мс реального времени при ×2 виртуальные часы должны уйти
		// заметно дальше старта; верхнюю границу не проверяем — CI бывает медленным.
		expect(clock.now()).toBeGreaterThan(1040)
		expect(clock.playing).toBe(false)

		const stopped = clock.now()
		await new Promise((resolve) => setTimeout(resolve, 20))
		expect(clock.now()).toBe(stopped)
	})

	it('seek сразу сообщает новое время подписчикам', () => {
		const clock = createReplayClock({ startAt: 0, tickMs: 1000 })
		let seen = -1
		clock.onTick((now) => {
			seen = now
		})

		clock.seek(500)

		expect(seen).toBe(500)
		expect(clock.now()).toBe(500)
	})

	it('игнорирует неположительную скорость', () => {
		const clock = createReplayClock({ speed: 1 })
		clock.setSpeed(0)
		expect(clock.speed).toBe(1)
		clock.setSpeed(-3)
		expect(clock.speed).toBe(1)
		clock.setSpeed(4)
		expect(clock.speed).toBe(4)
	})
})
