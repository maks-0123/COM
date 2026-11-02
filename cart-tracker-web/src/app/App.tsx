import { useEffect, useMemo, useState } from 'react'
import type { CSSProperties } from 'react'
import { countStale } from '../domain/status'
import type { PositionFix, ScenarioFile } from '../domain/types'
import { MapView } from '../features/map/MapView'
import { PollingFileSource } from '../sources/PollingFileSource'
import type { SourceHealth } from '../sources/PositionSource'
import { FileReplaySource } from '../sources/file/FileReplaySource'
import { createReplayClock } from '../sources/file/ReplayClock'
import { parseJsonScenario } from '../sources/file/parsers/parseJsonScenario'
import { readEmbedOptions } from './embed'
import type { EmbedTheme } from './embed'

// Два режима:
//   /                            — проигрывание записи (демо без сервера);
//   /?source=live                — опрос снимка раз в секунду;
//   /?embed=1&theme=dark&data=…  — то же самое, но для встраивания в NMS.

const SCENARIO_URL = 'data/demo-scenario.json'
const LIVE_URL = 'data/live-scenario.json'
const REPLAY_SPEED = 1

type LoadState =
	| { status: 'loading' }
	| { status: 'error'; errors: string[] }
	| { status: 'ready'; scenario: ScenarioFile }

type ModeProps = {
	theme: EmbedTheme
	/** Компактный режим: меньше плашка, без лишних полей. */
	compact: boolean
}

export default function App() {
	const state = useScenario(SCENARIO_URL)
	const options = readEmbedOptions(window.location.search)

	if (state.status === 'loading') {
		return <p style={{ padding: 16 }}>Загрузка {SCENARIO_URL}…</p>
	}
	if (state.status === 'error') {
		return (
			<div style={{ padding: 16 }}>
				<h3>Не удалось открыть {SCENARIO_URL}</h3>
				<ul>
					{state.errors.map(e => (
						<li key={e}>{e}</li>
					))}
				</ul>
			</div>
		)
	}

	return (
		// Leaflet нужна явная высота контейнера, иначе карта будет высотой 0 px.
		// position: fixed + inset: 0 растягивает блок на всё окно (или на весь iframe).
		<div
			style={{
				position: 'fixed',
				inset: 0,
				background: options.theme === 'dark' ? '#0f172a' : '#ffffff',
			}}
		>
			{options.sourceMode === 'live' ? (
				<Live
					scenario={state.scenario}
					dataUrl={options.dataUrl ?? LIVE_URL}
					theme={options.theme}
					compact={options.embed}
				/>
			) : (
				<Replay
					scenario={state.scenario}
					theme={options.theme}
					compact={options.embed}
				/>
			)}
		</div>
	)
}

/** Проигрывает сценарий и отдаёт карте текущую отметку каждой тележки. */
function Replay({
	scenario,
	theme,
	compact,
}: { scenario: ScenarioFile } & ModeProps) {
	const [positions, setPositions] = useState<Map<string, PositionFix>>(
		() => new Map(),
	)
	const [nowMs, setNowMs] = useState<number | null>(null)

	const { site, stations, carts } = scenario
	const { startMs, endMs } = useMemo(() => timeRange(scenario), [scenario])

	const staleCount = useMemo(
		() => (nowMs === null ? 0 : countStale(positions.values(), nowMs)),
		[positions, nowMs],
	)

	useEffect(() => {
		const clock = createReplayClock({ speed: REPLAY_SPEED })
		const source = new FileReplaySource(scenario, clock, { loop: true })

		const offFix = source.onFix(fix => {
			setPositions(prev => {
				const next = new Map(prev)
				next.set(fix.cartId, fix)
				return next
			})
		})
		const offReset = source.onReset(() => setPositions(new Map()))
		const offTick = clock.onTick(now => setNowMs(now))

		source.start()

		return () => {
			offFix()
			offReset()
			offTick()
			source.stop()
		}
	}, [scenario])

	return (
		<>
			<MapView
				site={site}
				stations={stations}
				carts={carts}
				positions={positions}
				nowMs={nowMs ?? startMs}
			/>
			<ReplayStatus
				nowMs={nowMs}
				startMs={startMs}
				endMs={endMs}
				staleCount={staleCount}
				totalCount={positions.size}
				theme={theme}
				compact={compact}
			/>
		</>
	)
}

/** Живой режим: сценарий-подложка из демо, координаты — опросом раз в секунду. */
function Live({
	scenario,
	dataUrl,
	theme,
	compact,
}: { scenario: ScenarioFile; dataUrl: string } & ModeProps) {
	const [positions, setPositions] = useState<Map<string, PositionFix>>(
		() => new Map(),
	)
	const [nowMs, setNowMs] = useState(() => Date.now())
	const [health, setHealth] = useState<SourceHealth>({ ok: true })

	const { site, stations, carts } = scenario

	useEffect(() => {
		const source = new PollingFileSource({ url: dataUrl })

		const offFix = source.onFix(fix => {
			setPositions(prev => {
				const next = new Map(prev)
				next.set(fix.cartId, fix)
				return next
			})
		})
		const offReset = source.onReset(() => setPositions(new Map()))
		const offHealth = source.onHealth(next => setHealth(next))

		source.start()
		const ticker = setInterval(() => setNowMs(Date.now()), 500)

		return () => {
			offFix()
			offReset()
			offHealth()
			clearInterval(ticker)
			source.stop()
		}
	}, [dataUrl])

	const staleCount = countStale(positions.values(), nowMs)

	return (
		<>
			<MapView
				site={site}
				stations={stations}
				carts={carts}
				positions={positions}
				nowMs={nowMs}
			/>
			<LiveStatus
				health={health}
				staleCount={staleCount}
				totalCount={positions.size}
				theme={theme}
				compact={compact}
			/>
		</>
	)
}

/** Границы записи в миллисекундах: по ним считается прогресс воспроизведения. */
function timeRange(scenario: ScenarioFile): { startMs: number; endMs: number } {
	if (scenario.fixes.length === 0) return { startMs: 0, endMs: 0 }

	let startMs = Number.POSITIVE_INFINITY
	let endMs = Number.NEGATIVE_INFINITY
	for (const fix of scenario.fixes) {
		const ts = Date.parse(fix.ts)
		if (ts < startMs) startMs = ts
		if (ts > endMs) endMs = ts
	}
	return { startMs, endMs }
}

/** Общий стиль плашки: учитывает тему и компактный режим. */
function badgeStyle(
	alert: boolean,
	theme: EmbedTheme,
	compact: boolean,
): CSSProperties {
	const dark = theme === 'dark'
	return {
		position: 'absolute',
		left: compact ? 8 : 12,
		bottom: compact ? 8 : 12,
		zIndex: 1000,
		padding: compact ? '4px 8px' : '6px 10px',
		border: `1px solid ${alert ? '#f59e0b' : dark ? '#334155' : '#cbd5e1'}`,
		borderRadius: compact ? 6 : 8,
		background: dark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(255, 255, 255, 0.92)',
		color: dark ? '#e2e8f0' : '#0f172a',
		font: `${compact ? 12 : 13}px/1.4 system-ui, sans-serif`,
	}
}

type StatusProps = ModeProps & {
	nowMs: number | null
	startMs: number
	endMs: number
	staleCount: number
	totalCount: number
}

/** Плашка записи: прогресс и предупреждение об устаревании. */
function ReplayStatus({
	nowMs,
	startMs,
	endMs,
	staleCount,
	totalCount,
	theme,
	compact,
}: StatusProps) {
	const elapsed = nowMs === null ? 0 : Math.max(0, nowMs - startMs) / 1000
	const total = Math.max(0, endMs - startMs) / 1000

	return (
		<div style={badgeStyle(staleCount > 0, theme, compact)}>
			<div>
				Запись: {elapsed.toFixed(1)} / {total.toFixed(1)} с
				{compact ? '' : ` · ×${REPLAY_SPEED}`}
			</div>
			{staleCount > 0 && (
				<div style={{ color: '#b45309' }}>
					Устарело: {staleCount} из {totalCount}
				</div>
			)}
		</div>
	)
}

type LiveStatusProps = ModeProps & {
	health: SourceHealth
	staleCount: number
	totalCount: number
}

/** Плашка живого режима: состояние связи и устаревание. */
function LiveStatus({
	health,
	staleCount,
	totalCount,
	theme,
	compact,
}: LiveStatusProps) {
	return (
		<div style={badgeStyle(!health.ok || staleCount > 0, theme, compact)}>
			<div>
				{health.ok
					? 'Живой режим · связь есть'
					: `Нет связи: ${health.message ?? 'ошибка'}`}
			</div>
			{staleCount > 0 && (
				<div style={{ color: '#b45309' }}>
					Устарело: {staleCount} из {totalCount}
				</div>
			)}
		</div>
	)
}

/** Скачивает и проверяет файл сценария. */
function useScenario(url: string): LoadState {
	const [state, setState] = useState<LoadState>({ status: 'loading' })

	useEffect(() => {
		const controller = new AbortController()

		fetch(url, { signal: controller.signal })
			.then(response => {
				if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
				return response.text()
			})
			.then(text => {
				const result = parseJsonScenario(text)
				setState(
					result.ok
						? { status: 'ready', scenario: result.scenario }
						: { status: 'error', errors: result.errors },
				)
			})
			.catch((e: Error) => {
				if (e.name !== 'AbortError')
					setState({ status: 'error', errors: [e.message] })
			})

		return () => controller.abort()
	}, [url])

	return state
}
