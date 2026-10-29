import { describe, expect, it } from 'vitest'
import { geoToLocal, localToGeo, METERS_PER_DEG_LAT } from './geo'

const ORIGIN = { lat: 55.9495, lon: 37.182 }

describe('localToGeo', () => {
	it('точка (0, 0) попадает ровно в origin', () => {
		expect(localToGeo({ x: 0, y: 0 }, ORIGIN)).toEqual(ORIGIN)
	})

	it('100 м на север — это +100/111320 градуса широты, долгота не меняется', () => {
		const geo = localToGeo({ x: 0, y: 100 }, ORIGIN)
		expect(geo.lat).toBeCloseTo(ORIGIN.lat + 100 / METERS_PER_DEG_LAT, 9)
		expect(geo.lon).toBeCloseTo(ORIGIN.lon, 9)
	})

	it('градус долготы на широте 56° короче градуса широты почти вдвое', () => {
		const geo = localToGeo({ x: 100, y: 0 }, ORIGIN)
		const dLon = geo.lon - ORIGIN.lon
		const dLat = 100 / METERS_PER_DEG_LAT
		// cos(55.95°) ≈ 0.56, значит сдвиг в градусах долготы больше в ~1.79 раза
		expect(dLon / dLat).toBeCloseTo(1 / Math.cos((ORIGIN.lat * Math.PI) / 180), 6)
	})

	it('при повороте сетки на 90° ось y площадки смотрит на восток', () => {
		const geo = localToGeo({ x: 0, y: 100 }, ORIGIN, 90)
		expect(geo.lat).toBeCloseTo(ORIGIN.lat, 9)
		expect(geo.lon).toBeGreaterThan(ORIGIN.lon)
	})
})

describe('geoToLocal', () => {
	it.each([
		{ x: 0, y: 0, rot: 0 },
		{ x: 20, y: 30, rot: 0 },
		{ x: 200, y: 0, rot: 0 },
		{ x: -150, y: 1200, rot: 37 },
	])('туда и обратно ($x, $y, поворот $rot°) — ошибка меньше 1 см', ({ x, y, rot }) => {
		const back = geoToLocal(localToGeo({ x, y }, ORIGIN, rot), ORIGIN, rot)
		expect(Math.abs(back.x - x)).toBeLessThan(0.01)
		expect(Math.abs(back.y - y)).toBeLessThan(0.01)
	})
})
