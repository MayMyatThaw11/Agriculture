import { BarChart3, CloudRain, Leaf, MapPinned, Sprout, TrendingUp } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext.jsx'

const overviewCards = [
	{
		key: 'dash.townships',
		value: '112',
		icon: MapPinned,
		accent: 'text-emerald-700',
		bg: 'bg-emerald-100',
	},
	{
		key: 'dash.records',
		value: '24,860',
		icon: BarChart3,
		accent: 'text-sky-700',
		bg: 'bg-sky-100',
	},
	{
		key: 'dash.yield',
		value: '3.6 t/ha',
		icon: Sprout,
		accent: 'text-amber-700',
		bg: 'bg-amber-100',
	},
	{
		key: 'dash.rainfall',
		value: '184 mm',
		icon: CloudRain,
		accent: 'text-indigo-700',
		bg: 'bg-indigo-100',
	},
]

const cropDistribution = [
	{ crop: 'Rice', percent: 42 },
	{ crop: 'Maize', percent: 23 },
	{ crop: 'Pulses', percent: 19 },
	{ crop: 'Sesame', percent: 16 },
]

const yieldByCrop = [
	{ crop: 'Rice', yield: 4.1 },
	{ crop: 'Maize', yield: 3.2 },
	{ crop: 'Pulses', yield: 2.6 },
	{ crop: 'Sesame', yield: 1.9 },
]

function Dashboard() {
	const { t } = useLanguage()

	return (
		<div className="space-y-6">
			<section className="rounded-[2rem] border border-white/80 bg-white/90 p-6 shadow-[0_20px_60px_rgba(12,46,61,0.08)] backdrop-blur-xl">
				<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div>
						<p className="text-xs font-semibold uppercase tracking-[0.4em] text-myanglow-medium">
							MyanGlow Analytics
						</p>
						<h2 className="mt-3 text-3xl font-semibold text-myanglow-navy">{t('dash.title')}</h2>
						<p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600 sm:text-base">
							{t('dash.subtitle')}
						</p>
					</div>

					<div className="inline-flex items-center gap-2 rounded-full border border-myanglow-sage bg-myanglow-sage/40 px-4 py-2 text-sm font-medium text-myanglow-darkGreen">
						<TrendingUp size={16} />
						Last 30 days trend
					</div>
				</div>
			</section>

			<section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
				{overviewCards.map((card) => {
					const Icon = card.icon
					return (
						<article
							key={card.key}
							className="rounded-[1.6rem] border border-white/80 bg-white/90 p-5 shadow-[0_14px_40px_rgba(12,46,61,0.08)] backdrop-blur-xl"
						>
							<div className="flex items-center justify-between gap-3">
								<p className="text-sm font-medium text-slate-500">{t(card.key)}</p>
								<span className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${card.bg} ${card.accent}`}>
									<Icon size={18} />
								</span>
							</div>
							<p className="mt-4 text-3xl font-semibold text-myanglow-navy">{card.value}</p>
						</article>
					)
				})}
			</section>

			<section className="grid gap-6 xl:grid-cols-2">
				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="mb-5 flex items-center gap-2 text-myanglow-navy">
						<Leaf size={18} />
						<h3 className="text-lg font-semibold">{t('dash.cropDist')}</h3>
					</div>

					<div className="space-y-4">
						{cropDistribution.map((item) => (
							<div key={item.crop} className="space-y-1">
								<div className="flex items-center justify-between text-sm">
									<span className="font-medium text-slate-700">{item.crop}</span>
									<span className="text-slate-500">{item.percent}%</span>
								</div>
								<div className="h-2 rounded-full bg-myanglow-sage/35">
									<div
										className="h-2 rounded-full bg-myanglow-forest"
										style={{ width: `${item.percent}%` }}
									/>
								</div>
							</div>
						))}
					</div>
				</article>

				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="mb-5 flex items-center gap-2 text-myanglow-navy">
						<BarChart3 size={18} />
						<h3 className="text-lg font-semibold">{t('dash.avgYieldCrop')}</h3>
					</div>

					<div className="space-y-3">
						{yieldByCrop.map((item) => (
							<div
								key={item.crop}
								className="flex items-center justify-between rounded-xl border border-myanglow-sage/50 bg-myanglow-sage/20 px-4 py-3"
							>
								<span className="font-medium text-slate-700">{item.crop}</span>
								<span className="text-sm font-semibold text-myanglow-navy">{item.yield} t/ha</span>
							</div>
						))}
					</div>
				</article>
			</section>
		</div>
	)
}

export default Dashboard
