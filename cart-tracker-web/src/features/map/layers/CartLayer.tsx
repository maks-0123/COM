import { CircleMarker, Tooltip } from 'react-leaflet'
import type { Cart, PositionFix, SiteConfig } from '../../../domain/types'
import { toLatLng } from '../projection'

// Цвет по умолчанию, если в файле у тележки нет своего color.
const DEFAULT_COLOR = '#2563eb'

type Props = {
	carts: Cart[]
	/** Последняя известная отметка каждой тележки: cartId -> отметка. */
	positions: Map<string, PositionFix>
	site: SiteConfig
}

export function CartLayer({ carts, positions, site }: Props) {
	return carts.map((cart) => {
		const fix = positions.get(cart.id)
		if (!fix) return null // отметок у тележки ещё не было — рисовать нечего

		const color = cart.color ?? DEFAULT_COLOR
		return (
			<CircleMarker
				key={cart.id}
				center={toLatLng(fix.position, site)}
				radius={7} // в пикселях: точка одного размера на любом масштабе
				pathOptions={{ color: '#fff', weight: 2, fillColor: color, fillOpacity: 1 }}
			>
				<Tooltip permanent direction='right' offset={[8, 0]}>
					{cart.name}
				</Tooltip>
			</CircleMarker>
		)
	})
}
