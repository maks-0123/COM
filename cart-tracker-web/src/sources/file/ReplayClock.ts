// Часы воспроизведения.
//
// Отделяют «когда выдавать отметку» от «как считать время»: источник спрашивает
// у часов текущий момент и сравнивает его с ts следующей отметки. Благодаря
// этому пауза, ускорение и перемотка не трогают сам источник, а тесты
// подставляют ручные часы и не ждут реальные секунды.

export type ClockListener = (nowMs: number) => void

export interface ReplayClock {
	readonly speed: number
	readonly playing: boolean
	/** Текущее виртуальное время, мс (обычно — эпоха из ts отметок). */
	now(): number
	start(): void
	pause(): void
	seek(nowMs: number): void
	setSpeed(speed: number): void
	/** Подписка на тики. Возвращает функцию отписки. */
	onTick(listener: ClockListener): () => void
}

export type ReplayClockOptions = {
	/** Начальная скорость: 1 — реальное время, 2 — вдвое быстрее. */
	speed?: number
	/** Период тика, мс: 50 даёт плавное движение без лишней нагрузки. */
	tickMs?: number
	/** Стартовое виртуальное время, мс. */
	startAt?: number
}

const DEFAULT_TICK_MS = 50

/** Часы на performance.now: виртуальное время идёт со множителем speed. */
export function createReplayClock(options: ReplayClockOptions = {}): ReplayClock {
	let speed = options.speed !== undefined && options.speed > 0 ? options.speed : 1
	const tickMs = options.tickMs !== undefined && options.tickMs > 0 ? options.tickMs : DEFAULT_TICK_MS

	let virtualNow = options.startAt ?? 0
	let anchorReal = 0
	let anchorVirtual = virtualNow
	let playing = false
	let timer: ReturnType<typeof setInterval> | undefined
	const listeners = new Set<ClockListener>()

	const emit = () => {
		for (const listener of listeners) listener(virtualNow)
	}

	const rebase = () => {
		anchorReal = performance.now()
		anchorVirtual = virtualNow
	}

	const tick = () => {
		if (!playing) return
		virtualNow = anchorVirtual + (performance.now() - anchorReal) * speed
		emit()
	}

	return {
		get speed() {
			return speed
		},
		get playing() {
			return playing
		},
		now: () => virtualNow,
		start() {
			if (playing) return
			playing = true
			rebase()
			tick()
			timer = setInterval(tick, tickMs)
		},
		pause() {
			if (!playing) return
			tick() // зафиксировать накопленное время до остановки
			playing = false
			if (timer !== undefined) clearInterval(timer)
			timer = undefined
		},
		seek(next) {
			virtualNow = next
			rebase()
			emit()
		},
		setSpeed(next) {
			if (next <= 0 || !Number.isFinite(next)) return
			tick() // накопить время по старой скорости
			speed = next
			rebase()
		},
		onTick(listener) {
			listeners.add(listener)
			return () => {
				listeners.delete(listener)
			}
		},
	}
}
