import type { LatLngTuple } from 'leaflet'
import { useEffect, useState } from 'react'
import { MapContainer, useMap } from 'react-leaflet'
import type { PositionFix, ScenarioFile } from '../domain/types'
import { SiteBasemap } from '../features/map/basemaps'
import { CartLayer } from '../features/map/layers/CartLayer'
import { StationLayer } from '../features/map/layers/StationLayer'
import { toLatLng } from '../features/map/projection'
import { parseJsonScenario } from '../sources/file/parsers/parseJsonScenario'

// ВРЕМЕННО: файл загружается прямо в App, тележки стоят на первой отметке.
// Дальше загрузка переедет в FileReplaySource (проигрывание во времени),
// а карта — в features/map/MapView.tsx.
const SCENARIO_URL = '/data/demo-scenario.json'

type LoadState =
	| { status: 'loading' }
	| { status: 'error'; errors: string[] }
	| { status: 'ready'; scenario: ScenarioFile }

export default function App() {
	const state = useScenario(SCENARIO_URL)

	if (state.status === 'loading') {
		return <p style={{ padding: 16 }}>Загрузка {SCENARIO_URL}…</p>
	}
	if (state.status === 'error') {
		return (
			<div style={{ padding: 16 }}>
				<h3>Не удалось открыть {SCENARIO_URL}</h3>
				<ul>
					{state.errors.map((e) => (
						<li key={e}>{e}</li>
					))}
				</ul>
			</div>
		)
	}

	const { site, stations, carts, fixes } = state.scenario
	const stationPoints = stations.map((s) => toLatLng(s.position, site))

	return (
		// Leaflet нужна явная высота контейнера, иначе карта будет высотой 0 px.
		// position: fixed + inset: 0 растягивает блок на всё окно браузера.
		<div style={{ position: 'fixed', inset: 0 }}>
			<MapContainer
				center={stationPoints[0] ?? [0, 0]}
				zoom={17}
				maxZoom={20}
				// Без плашки «Leaflet» в правом нижнем углу.
				attributionControl={false}
				style={{ height: '100%', width: '100%' }}
			>
				{site.basemap.type === 'pmtiles' && <SiteBasemap url={site.basemap.url} />}
				<FitToPoints points={stationPoints} />
				<StationLayer stations={stations} site={site} />
				<CartLayer carts={carts} positions={firstFixPerCart(fixes)} site={site} />
			</MapContainer>
		</div>
	)
}

/** Скачивает и проверяет файл сценария. */
function useScenario(url: string): LoadState {
	const [state, setState] = useState<LoadState>({ status: 'loading' })

	useEffect(() => {
		// AbortController отменяет загрузку, если компонент убрали со страницы
		// раньше, чем пришёл ответ (StrictMode так делает при разработке).
		const controller = new AbortController()

		fetch(url, { signal: controller.signal })
			.then((response) => {
				if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
				return response.text()
			})
			.then((text) => {
				const result = parseJsonScenario(text)
				setState(
					result.ok
						? { status: 'ready', scenario: result.scenario }
						: { status: 'error', errors: result.errors },
				)
			})
			.catch((e: Error) => {
				if (e.name !== 'AbortError') setState({ status: 'error', errors: [e.message] })
			})

		return () => controller.abort()
	}, [url])

	return state
}

/** Первая по времени отметка каждой тележки (fixes уже упорядочены по ts). */
function firstFixPerCart(fixes: PositionFix[]): Map<string, PositionFix> {
	const result = new Map<string, PositionFix>()
	for (const fix of fixes) {
		if (!result.has(fix.cartId)) result.set(fix.cartId, fix)
	}
	return result
}

/** Один раз при открытии подбирает масштаб так, чтобы все точки были видны. */
function FitToPoints({ points }: { points: LatLngTuple[] }) {
	const map = useMap()
	useEffect(() => {
		if (points.length > 0) map.fitBounds(points, { padding: [60, 60] })
		// points намеренно не в зависимостях: подгоняем только при открытии,
		// дальше масштабом управляет пользователь.
	}, [map])
	return null
}
