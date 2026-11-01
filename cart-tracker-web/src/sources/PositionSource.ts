import type { PositionFix } from '../domain/types'

// Порт источника отметок: карте всё равно, откуда приходят координаты.
// Сейчас это проигрывание записанного файла, позже — WebSocket от Magma.
// Домен и карта работают только с этим интерфейсом.

export type SourceState = 'idle' | 'playing' | 'ended'

export type FixListener = (fix: PositionFix) => void
export type ResetListener = () => void

export interface PositionSource {
	readonly state: SourceState
	/** Начать выдачу отметок. Повторный вызов во время работы ничего не делает. */
	start(): void
	/** Остановить выдачу и освободить ресурсы. */
	stop(): void
	/** Подписка на отметки. Возвращает функцию отписки. */
	onFix(listener: FixListener): () => void
	/** Подписка на сброс: слушатель должен забыть накопленные позиции. */
	onReset(listener: ResetListener): () => void
}
