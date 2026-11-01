import { CircleMarker, Tooltip } from 'react-leaflet'
import { ageMs, freshness } from '../../../domain/status'
import type { Cart, PositionFix, SiteConfig } from '../../../domain/types'
import { methodLabel } from '../accuracy'
import { toLatLng } from '../projection'

// Цвет по умолчанию, если в файле у тележки нет своего color.
const DEFAULT_COLOR = '#2563eb'
// Устаревшая тележка: серый пунктир вместо цветной точки.
const STALE_COLOR = '#94a3b8'

type Props = {
	carts: Cart[]
	/** Последняя известная отметка каждой тележки: cartId -> отметка. */
	positions: Map<string, PositionFix>
	site: SiteConfig
	/** Текущее время источника: по нему считается свежесть отметок. */
	nowMs: number
}

export function CartLayer({ carts, positions, site, nowMs }: Props) {
	return carts.map((cart) => {
		const fix = positions.get(cart.id)
		if (!fix) return null // отметок у тележки ещё не было — рисовать нечего

		const stale = freshness(fix, nowMs) === 'stale'
		const color = stale ? STALE_COLOR : (cart.color ?? DEFAULT_COLOR)
		const ageS = Math.max(0, ageMs(fix, nowMs)) / 1000

		const details = [cart.name]
		if (fix.method) details.push(methodLabel(fix.method))
		if (fix.accuracyM !== undefined) details.push(`±${Math.round(fix.accuracyM)} м`)
		if (stale) details.push(`нет данных ${ageS.toFixed(1)} с`)

		return (
			<CircleMarker
				key={cart.id}
				center={toLatLng(fix.position, site)}
				// В пикселях: точка одного размера на любом масштабе.
				// Устаревшая чуть меньше и полупрозрачная.
				radius={stale ? 6 : 7}
				pathOptions={{
					color: '#fff',
					weight: 2,
					fillColor: color,
					fillOpacity: stale ? 0.45 : 1,
					dashArray: stale ? '4 3' : undefined,
				}}
			>
				<Tooltip permanent direction='right' offset={[8, 0]}>
					{details.join(' · ')}
				</Tooltip>
			</CircleMarker>
		)
	})
}
