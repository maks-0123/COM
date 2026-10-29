import { z } from 'zod'
import type { ScenarioFile } from './types'

// Проверка файла сценария библиотекой zod.
//
// types.ts говорит TypeScript, какими данные ДОЛЖНЫ быть, но во время работы
// программы эти типы исчезают. Файл приходит снаружи, и в нём может быть
// что угодно. Схема ниже проверяет файл на самом деле и в случае ошибки
// говорит, где именно она: "fixes[3].position: ...".

const LocalPointSchema = z.object({ x: z.number(), y: z.number() })

const GeoPointSchema = z.object({
	lat: z.number().min(-90).max(90),
	lon: z.number().min(-180).max(180),
})

const PointSchema = z.union([LocalPointSchema, GeoPointSchema], {
	error: 'ожидается точка {x, y} в метрах или {lat, lon} в градусах',
})

const BasemapSchema = z.discriminatedUnion('type', [
	z.object({ type: z.literal('pmtiles'), url: z.string() }),
	z.object({ type: z.literal('osm'), tileUrl: z.string().optional() }),
	z.object({
		type: z.literal('image'),
		url: z.string(),
		widthM: z.number().positive(),
		heightM: z.number().positive(),
	}),
	z.object({ type: z.literal('none') }),
])

const SiteSchema = z.object({
	id: z.string().min(1),
	name: z.string(),
	coordinateSystem: z.enum(['local', 'wgs84']),
	origin: GeoPointSchema.optional(),
	rotationDeg: z.number().optional(),
	basemap: BasemapSchema,
})

const StationSchema = z.object({
	id: z.string().min(1),
	name: z.string(),
	position: PointSchema,
	heightM: z.number().optional(),
	enodebSerial: z.string().optional(),
	cellIds: z.array(z.string()).optional(),
})

const CartSchema = z.object({
	id: z.string().min(1),
	name: z.string(),
	type: z.string().optional(),
	color: z.string().optional(),
	imsi: z.string().optional(),
})

const PositionFixSchema = z.object({
	cartId: z.string().min(1),
	ts: z.string().refine((s) => !Number.isNaN(Date.parse(s)), {
		error: 'ожидается дата в формате ISO-8601, например 2026-10-28T09:00:00Z',
	}),
	position: PointSchema,
	accuracyM: z.number().min(0).optional(),
	method: z
		.enum(['rssi-multilateration', 'ecid-ta', 'cell-id', 'simulated', 'unknown'])
		.optional(),
	speedMps: z.number().min(0).optional(),
	headingDeg: z.number().min(0).lt(360).optional(),
	stationsUsed: z.array(z.string()).optional(),
	truth: PointSchema.optional(),
})

// Аннотация z.ZodType<ScenarioFile> заставляет TypeScript сверить схему
// с типами из types.ts: если они разойдутся, проект не соберётся.
export const ScenarioSchema: z.ZodType<ScenarioFile> = z
	.object({
		schemaVersion: z.literal(1, {
			error: 'поддерживается только schemaVersion: 1',
		}),
		site: SiteSchema,
		stations: z.array(StationSchema),
		carts: z.array(CartSchema),
		fixes: z.array(PositionFixSchema),
	})
	// Проверки, которые смотрят на несколько полей сразу.
	.superRefine((file, ctx) => {
		const { site } = file
		const isLocal = site.coordinateSystem === 'local'
		const onMap = site.basemap.type === 'pmtiles' || site.basemap.type === 'osm'

		if (isLocal && onMap && !site.origin) {
			ctx.addIssue({
				code: 'custom',
				path: ['site', 'origin'],
				message: 'для local-координат на карте нужен origin — где на Земле точка (0, 0)',
			})
		}

		// Все точки должны быть в той же системе, что и площадка.
		const expected = isLocal ? '{x, y}' : '{lat, lon}'
		const checkPoint = (point: object | undefined, path: (string | number)[]) => {
			if (point && 'lat' in point === isLocal) {
				ctx.addIssue({
					code: 'custom',
					path,
					message: `ожидается ${expected}, потому что site.coordinateSystem = ${site.coordinateSystem}`,
				})
			}
		}
		file.stations.forEach((s, i) => checkPoint(s.position, ['stations', i, 'position']))
		file.fixes.forEach((f, i) => {
			checkPoint(f.position, ['fixes', i, 'position'])
			checkPoint(f.truth, ['fixes', i, 'truth'])
		})

		// id не повторяются.
		const checkUnique = (items: { id: string }[], key: 'stations' | 'carts') => {
			const seen = new Set<string>()
			items.forEach((item, i) => {
				if (seen.has(item.id)) {
					ctx.addIssue({
						code: 'custom',
						path: [key, i, 'id'],
						message: `id "${item.id}" уже встречался выше`,
					})
				}
				seen.add(item.id)
			})
		}
		checkUnique(file.stations, 'stations')
		checkUnique(file.carts, 'carts')

		// Каждая отметка относится к известной тележке.
		const cartIds = new Set(file.carts.map((c) => c.id))
		file.fixes.forEach((f, i) => {
			if (!cartIds.has(f.cartId)) {
				ctx.addIssue({
					code: 'custom',
					path: ['fixes', i, 'cartId'],
					message: `тележки "${f.cartId}" нет в списке carts`,
				})
			}
		})
	})
