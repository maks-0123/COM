import { describe, expect, it } from 'vitest'
import example from '../../../domain/__fixtures__/scenario.example.json'
import { parseJsonScenario } from './parseJsonScenario'

// Копия примера, которую каждый тест портит по-своему.
const clone = () => structuredClone(example) as Record<string, any>
const parse = (data: unknown) => parseJsonScenario(JSON.stringify(data))

describe('parseJsonScenario', () => {
	it('пример файла разбирается без ошибок', () => {
		const result = parse(example)
		expect(result.ok).toBe(true)
		if (result.ok) {
			expect(result.scenario.stations).toHaveLength(3)
			expect(result.scenario.carts).toHaveLength(2)
		}
	})

	it('отметки упорядочены по времени, даже если в файле перемешаны', () => {
		const data = clone()
		data.fixes.reverse()
		const result = parse(data)
		if (!result.ok) throw new Error(result.errors.join('\n'))
		const times = result.scenario.fixes.map((f) => Date.parse(f.ts))
		expect(times).toEqual([...times].sort((a, b) => a - b))
	})

	it('сломанный JSON — понятная ошибка, а не падение', () => {
		const result = parseJsonScenario('{ "schemaVersion": 1, ')
		expect(result).toMatchObject({ ok: false })
		if (!result.ok) expect(result.errors[0]).toMatch(/не является JSON/)
	})

	it('точка в градусах на local-площадке отклоняется с путём к полю', () => {
		const data = clone()
		data.fixes[3].position = { lat: 55.95, lon: 37.18 }
		const result = parse(data)
		expect(result.ok).toBe(false)
		if (!result.ok) {
			expect(result.errors).toContain(
				'fixes[3].position: ожидается {x, y}, потому что site.coordinateSystem = local',
			)
		}
	})

	it('неизвестная тележка и повтор id станции находятся', () => {
		const data = clone()
		data.fixes[0].cartId = 'cart-99'
		data.stations[1].id = 'bs-1'
		const result = parse(data)
		if (result.ok) throw new Error('файл должен быть отклонён')
		expect(result.errors.join('\n')).toMatch(/fixes\[0\]\.cartId: тележки "cart-99"/)
		expect(result.errors.join('\n')).toMatch(/stations\[1\]\.id: id "bs-1"/)
	})

	it('без origin local-координаты на карту не положить', () => {
		const data = clone()
		delete data.site.origin
		const result = parse(data)
		if (result.ok) throw new Error('файл должен быть отклонён')
		expect(result.errors.join('\n')).toMatch(/site\.origin/)
	})
})
