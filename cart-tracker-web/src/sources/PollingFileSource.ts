import type { PositionFix, ScenarioFile } from '../domain/types'
import { parseJsonScenario } from './file/parsers/parseJsonScenario'
import type {
	FixListener,
	HealthListener,
	PositionSource,
	ResetListener,
	SourceHealth,
	SourceState,
} from './PositionSource'

// Живой источник: раз в секунду забирает JSON-снимок по HTTP.
//
// Снимок полный (сценарий целиком), но наружу выдаются только новые отметки:
// сравниваем ts с последней выданной по каждой тележке. Первый снимок даёт
// по одной, самой свежей отметке на тележку, чтобы карта заполнилась сразу,
// а не проигрывала историю.
//
// Ошибки сети и битый JSON не роняют источник: он сообщает onHealth и
// продолжает опрос, сохраняя последние известные позиции.

export type PollingOptions = {
	url: string
	/** Период опроса, мс. */
	intervalMs?: number
	/** Подмена fetch в тестах. */
	fetchImpl?: typeof fetch
}

export class PollingFileSource implements PositionSource {
	readonly #url: string
	readonly #intervalMs: number
	readonly #fetchImpl: typeof fetch

	readonly #fixListeners = new Set<FixListener>()
	readonly #resetListeners = new Set<ResetListener>()
	readonly #healthListeners = new Set<HealthListener>()

	#state: SourceState = 'idle'
	#timer: ReturnType<typeof setInterval> | undefined
	#inFlight = false
	#lastTs = new Map<string, number>()
	#siteId: string | null = null
	#lastHealth: SourceHealth | null = null

	constructor(options: PollingOptions) {
		this.#url = options.url
		this.#intervalMs = options.intervalMs ?? 1000
		this.#fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis)
	}

	get state(): SourceState {
		return this.#state
	}

	start(): void {
		if (this.#state === 'playing') return
		this.#state = 'playing'
		void this.poll()
		this.#timer = setInterval(() => void this.poll(), this.#intervalMs)
	}

	stop(): void {
		if (this.#timer !== undefined) clearInterval(this.#timer)
		this.#timer = undefined
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

	onHealth(listener: HealthListener): () => void {
		this.#healthListeners.add(listener)
		return () => {
			this.#healthListeners.delete(listener)
		}
	}

	/** Один цикл опроса. Публичный, чтобы тесты и отладка не ждали таймера. */
	async poll(): Promise<void> {
		if (this.#inFlight) return
		this.#inFlight = true
		try {
			const response = await this.#fetchImpl(this.#url, { cache: 'no-store' })
			if (!response.ok) throw new Error(`сервер ответил ${response.status}`)

			const result = parseJsonScenario(await response.text())
			if (!result.ok) {
				this.#report({ ok: false, message: result.errors.join('; ') })
				return
			}

			this.#apply(result.scenario)
			this.#report({ ok: true })
		} catch (error) {
			this.#report({ ok: false, message: (error as Error).message })
		} finally {
			this.#inFlight = false
		}
	}

	#apply(scenario: ScenarioFile): void {
		// Сменилась площадка — забываем всё, что знали о прошлой.
		if (this.#siteId !== null && this.#siteId !== scenario.site.id) {
			this.#lastTs.clear()
			this.#emitReset()
		}
		this.#siteId = scenario.site.id

		const fresh = [...scenario.fixes].sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts))

		if (this.#lastTs.size === 0) {
			// Первый снимок: по одной самой новой отметке на тележку,
			// в хронологическом порядке.
			const latest = new Map<string, PositionFix>()
			for (const fix of fresh) latest.set(fix.cartId, fix)
			const first = [...latest.values()].sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts))
			for (const fix of first) {
				this.#lastTs.set(fix.cartId, Date.parse(fix.ts))
				this.#emitFix(fix)
			}
			return
		}

		for (const fix of fresh) {
			const ts = Date.parse(fix.ts)
			if (ts <= (this.#lastTs.get(fix.cartId) ?? Number.NEGATIVE_INFINITY)) continue
			this.#lastTs.set(fix.cartId, ts)
			this.#emitFix(fix)
		}
	}

	#emitFix(fix: PositionFix): void {
		for (const listener of this.#fixListeners) listener(fix)
	}

	#emitReset(): void {
		for (const listener of this.#resetListeners) listener()
	}

	/** Сообщает о связи только при изменении, чтобы не дёргать React зря. */
	#report(next: SourceHealth): void {
		const previous = this.#lastHealth
		if (previous && previous.ok === next.ok && previous.message === next.message) return
		this.#lastHealth = next
		for (const listener of this.#healthListeners) listener(next)
	}
}
