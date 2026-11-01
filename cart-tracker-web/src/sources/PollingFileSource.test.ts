import { describe, expect, it } from 'vitest'
import type { PositionFix, ScenarioFile } from '../domain/types'
import { PollingFileSource } from './PollingFileSource'
import type { SourceHealth } from './PositionSource'

const T0 = Date.parse('2026-10-28T09:00:00Z')

function fix(cartId: string, offsetMs: number): PositionFix {
	return { cartId, ts: new Date(T0 + offsetMs).toISOString(), position: { x: offsetMs / 1000, y: 0 } }
}

function scenario(fixes: PositionFix[], siteId = 'site-1'): ScenarioFile {
	return {
		schemaVersion: 1,
		generatedAt: new Date(T0).toISOString(),
		site: {
			id: siteId,
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

function okResponse(body: ScenarioFile | string): Response {
	return {
		ok: true,
		status: 200,
		text: async () => (typeof body === 'string' ? body : JSON.stringify(body)),
	} as unknown as Response
}

function failResponse(status = 500): Response {
	return { ok: false, status, text: async () => '' } as unknown as Response
}

function setup(responses: Response[]) {
	let call = 0
	const seen: string[] = []
	const health: SourceHealth[] = []
	let resets = 0

	const source = new PollingFileSource({
		url: '/data/live-scenario.json',
		fetchImpl: async () => {
			const index = Math.min(call, responses.length - 1)
			call += 1
			return responses[index] ?? failResponse()
		},
	})

	// Каждый poll() берёт следующий ответ; лишние повторы — последний.
	const next = async () => {
		await source.poll()
	}

	source.onFix((f) => seen.push(`${f.cartId}@${Date.parse(f.ts) - T0}`))
	source.onReset(() => {
		resets += 1
	})
	source.onHealth((h) => health.push(h))

	return { source, seen, health, resets: () => resets, next }
}

describe('PollingFileSource', () => {
	it('первый снимок даёт по одной свежей отметке на тележку', async () => {
		const { seen, next } = setup([okResponse(scenario([fix('c1', 0), fix('c1', 1000), fix('c2', 500)]))])

		await next()

		expect(seen).toEqual(['c2@500', 'c1@1000'])
	})

	it('следующий снимок выдаёт только новые отметки', async () => {
		const { seen, next } = setup([
			okResponse(scenario([fix('c1', 0), fix('c1', 1000)])),
			okResponse(scenario([fix('c1', 0), fix('c1', 1000), fix('c2', 1500), fix('c1', 2000)])),
		])

		await next()
		await next()

		expect(seen).toEqual(['c1@1000', 'c2@1500', 'c1@2000'])
	})

	it('повторный тот же снимок не добавляет отметок', async () => {
		const snapshot = scenario([fix('c1', 0), fix('c1', 1000)])
		const { seen, next } = setup([okResponse(snapshot)])

		await next()
		const afterFirst = [...seen]
		await next()

		expect(seen).toEqual(afterFirst)
	})

	it('смена площадки сбрасывает накопленные позиции', async () => {
		const { seen, resets, next } = setup([
			okResponse(scenario([fix('c1', 0), fix('c2', 500)], 'site-1')),
			okResponse(scenario([fix('c1', 0), fix('c2', 500)], 'site-2')),
		])

		await next()
		await next()

		expect(resets()).toBe(1)
		expect(seen).toEqual(['c1@0', 'c2@500', 'c1@0', 'c2@500'])
	})

	it('ошибка сети не роняет источник и видна в health', async () => {
		const { health, next } = setup([okResponse(scenario([fix('c1', 0)])), failResponse(503)])

		await next()
		await expect(next()).resolves.toBeUndefined()

		expect(health).toEqual([{ ok: true }, { ok: false, message: 'сервер ответил 503' }])
	})

	it('битый JSON сообщает об ошибке, но не выбрасывает исключение', async () => {
		const { health, seen, next } = setup([okResponse(scenario([fix('c1', 0)])), okResponse('не json')])

		await next()
		await expect(next()).resolves.toBeUndefined()

		expect(seen).toEqual(['c1@0'])
		expect(health.at(-1)?.ok).toBe(false)
		expect(health.at(-1)?.message).toContain('JSON')
	})

	it('после обрыва связь восстанавливается и новые отметки приходят', async () => {
		const { health, seen, next } = setup([
			okResponse(scenario([fix('c1', 0)])),
			failResponse(500),
			okResponse(scenario([fix('c1', 0), fix('c1', 1000)])),
		])

		await next()
		await next()
		await next()

		expect(health.map((h) => h.ok)).toEqual([true, false, true])
		expect(seen).toEqual(['c1@0', 'c1@1000'])
	})
})
