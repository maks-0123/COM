import type { GeoPoint, LocalPoint } from './types'

// Пересчёт «метры площадки» <-> «широта/долгота».
//
// Считаем Землю плоской в пределах площадки. На расстоянии нескольких
// километров ошибка — сантиметры, это намного меньше точности
// позиционирования по сигналу (метры и десятки метров).

/** Сколько метров в одном градусе широты (почти одинаково по всей Земле). */
export const METERS_PER_DEG_LAT = 111_320

const toRad = (deg: number) => (deg * Math.PI) / 180

/** Метров в одном градусе долготы на данной широте: к полюсам меньше. */
function metersPerDegLon(lat: number): number {
	return METERS_PER_DEG_LAT * Math.cos(toRad(lat))
}

/**
 * Локальная точка (метры) -> точка на Земле.
 * rotationDeg — на сколько градусов по часовой стрелке ось y площадки
 * отклонена от истинного севера (0 — сетка смотрит строго на север).
 */
export function localToGeo(
	point: LocalPoint,
	origin: GeoPoint,
	rotationDeg = 0,
): GeoPoint {
	// 1. Поворачиваем оси площадки, чтобы получить метры на восток и на север.
	const a = toRad(rotationDeg)
	const east = point.x * Math.cos(a) + point.y * Math.sin(a)
	const north = -point.x * Math.sin(a) + point.y * Math.cos(a)

	// 2. Метры -> градусы вокруг origin.
	return {
		lat: origin.lat + north / METERS_PER_DEG_LAT,
		lon: origin.lon + east / metersPerDegLon(origin.lat),
	}
}

/** Обратный пересчёт: точка на Земле -> метры площадки. */
export function geoToLocal(
	point: GeoPoint,
	origin: GeoPoint,
	rotationDeg = 0,
): LocalPoint {
	const east = (point.lon - origin.lon) * metersPerDegLon(origin.lat)
	const north = (point.lat - origin.lat) * METERS_PER_DEG_LAT

	// Поворот в обратную сторону.
	const a = toRad(rotationDeg)
	return {
		x: east * Math.cos(a) - north * Math.sin(a),
		y: east * Math.sin(a) + north * Math.cos(a),
	}
}
