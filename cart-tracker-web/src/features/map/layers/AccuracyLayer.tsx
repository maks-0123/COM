import { Circle } from 'react-leaflet'
import type { PositionFix, SiteConfig } from '../../../domain/types'
import { accuracyStyle } from '../accuracy'
import { toLatLng } from '../projection'

// Круги неопределённости вокруг тележек.
//
// Радиус берётся из accuracyM (в метрах), внешний вид — из accuracyStyle:
// цвет по методу, прозрачность по свежести. Слой неинтерактивный, чтобы
// не перехватывать клики по карте, и рисуется до станций и тележек.

type Props = {
	positions: Map<string, PositionFix>
	site: SiteConfig
	nowMs: number
}

export function AccuracyLayer({ positions, site, nowMs }: Props) {
	return [...positions.values()].map((fix) => {
		const accuracyM = fix.accuracyM
		// Нет точности или она вырождена — круг не рисуем.
		if (accuracyM === undefined || accuracyM <= 0) return null

		const style = accuracyStyle(fix, nowMs)
		if (style === null) return null

		return (
			<Circle
				key={fix.cartId}
				center={toLatLng(fix.position, site)}
				radius={accuracyM}
				interactive={false}
				pathOptions={style}
			/>
		)
	})
}
