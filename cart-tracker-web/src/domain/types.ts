// Контракты данных: как выглядят станции, тележки и отметки положения.
// Описание полей и зачем они нужны — ARCHITECTURE.md, раздел 6.
//
// Здесь только типы: никакого кода, который что-то делает, и никаких
// импортов из React или Leaflet. Эти типы общие для всего приложения —
// и для файла, и для будущего живого источника (WebSocket от Magma).

// ---------- Координаты ----------

/** Точка в метрах от начала площадки: x — на восток, y — на север. */
export type LocalPoint = { x: number; y: number }

/** Точка на Земле в градусах WGS-84 (как в GPS). */
export type GeoPoint = { lat: number; lon: number }

/** Любая точка. Какая именно — решает site.coordinateSystem. */
export type Point = LocalPoint | GeoPoint

/** Отличает GeoPoint от LocalPoint по наличию поля lat. */
export function isGeoPoint(point: Point): point is GeoPoint {
	return 'lat' in point
}

// ---------- Площадка ----------

export type CoordinateSystem = 'local' | 'wgs84'

export type Basemap =
	| { type: 'pmtiles'; url: string } // своя карта из файла .pmtiles
	| { type: 'osm'; tileUrl?: string } // картинки-тайлы с сервера
	| { type: 'image'; url: string; widthM: number; heightM: number } // план цеха
	| { type: 'none' } // пустой фон

export type SiteConfig = {
	id: string
	name: string
	coordinateSystem: CoordinateSystem
	/** Где на Земле лежит локальная точка (0, 0). Нужна для local + карта. */
	origin?: GeoPoint
	/** Поворот сетки площадки от истинного севера по часовой стрелке, градусы. */
	rotationDeg?: number
	basemap: Basemap
}

// ---------- Станции и тележки ----------

export type Station = {
	id: string // постоянный id, например "bs-1"
	name: string
	position: Point
	heightM?: number
	enodebSerial?: string // связь с eNodeB в Magma (на будущее)
	cellIds?: string[]
}

export type Cart = {
	id: string // постоянный id, например "cart-01"
	name: string
	type?: string // "forklift", "tugger", ...
	color?: string
	imsi?: string // связь с абонентом в Magma (на будущее)
}

// ---------- Отметки положения ----------

export type PositioningMethod =
	| 'rssi-multilateration' // 3+ станции, основной метод
	| 'ecid-ta' // 2 станции + Timing Advance
	| 'cell-id' // 1 станция: «где-то рядом с ней»
	| 'simulated' // сгенерированные тестовые данные
	| 'unknown'

export type PositionFix = {
	cartId: string
	/** Время в ISO-8601 UTC, например "2026-10-28T09:00:01Z". */
	ts: string
	position: Point
	/** Радиус круга неопределённости, метры. */
	accuracyM?: number
	method?: PositioningMethod
	speedMps?: number
	/** Курс: 0 — север, по часовой стрелке. */
	headingDeg?: number
	stationsUsed?: string[]
	/** Только симулятор: где тележка была на самом деле. */
	truth?: Point
}

// ---------- Файл сценария ----------

export type ScenarioFile = {
	schemaVersion: 1
	site: SiteConfig
	stations: Station[]
	carts: Cart[]
	fixes: PositionFix[]
}
