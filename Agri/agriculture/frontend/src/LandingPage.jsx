import {
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronDown,
  Leaf,
  LineChart,
  Radar,
  RadioTower,
  ScanSearch,
  Sparkles,
  Sprout,
} from 'lucide-react'
import { Link } from 'react-router-dom'

const capabilities = [
  {
    icon: Radar,
    title: 'Satellite crop intelligence',
    description: 'Turn NDVI vegetation signals into clear field-health insights and seasonal trends.',
  },
  {
    icon: Sprout,
    title: 'Smart crop recommendations',
    description: 'Match soil, rainfall, and temperature conditions with suitable crops and yield estimates.',
  },
  {
    icon: ScanSearch,
    title: 'Plant disease detection',
    description: 'Upload a leaf image and receive an easy-to-understand health assessment and guidance.',
  },
  {
    icon: Bot,
    title: 'Agriculture AI assistant',
    description: 'Give farmers one place to ask questions and make confident, data-supported decisions.',
  },
  {
    icon: RadioTower,
    title: 'IoT sensor simulation',
    description: 'Monitor simulated soil moisture, pH, and light readings through live charts and sensor status updates.',
  },
]

const signals = [
  { label: 'Vegetation health', value: '0.71', icon: Leaf },
  { label: 'Crop condition match', value: '94%', icon: Sparkles },
  { label: 'Field insights', value: 'Live', icon: LineChart },
]

function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-gradient-to-br from-myanglow-sage via-white to-myanglow-soft/40 text-myanglow-navy">
      <section className="relative min-h-screen">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(154,214,76,0.28),transparent_25%),radial-gradient(circle_at_88%_12%,rgba(90,176,63,0.18),transparent_24%),radial-gradient(circle_at_65%_88%,rgba(161,188,178,0.28),transparent_30%)]" />
        <div className="absolute -left-20 top-52 h-56 w-56 rounded-full border border-myanglow-soft/30" />
        <div className="absolute -left-12 top-60 h-40 w-40 rounded-full border border-myanglow-soft/30" />

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex w-full items-center justify-between py-8">
            <div className="flex items-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-2xl bg-myanglow-forest text-white shadow-lg shadow-myanglow-forest/20">
                <Leaf size={22} />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.5em] text-myanglow-medium">MyanGlow</p>
                <p className="text-xs text-slate-500">Intelligence for every field</p>
              </div>
            </div>

            <div className="hidden items-center gap-8 text-sm font-medium text-slate-600 md:flex lg:gap-10">
              <a href="#capabilities" className="transition hover:text-myanglow-forest">Capabilities</a>
              <a href="#impact" className="transition hover:text-myanglow-forest">Impact</a>
              <Link to="/dashboard" className="rounded-xl bg-myanglow-forest px-5 py-3 text-white shadow-lg shadow-myanglow-forest/15 transition hover:bg-myanglow-medium">
                Open platform
              </Link>
            </div>
          </nav>

          <div className="grid min-h-[calc(100vh-7rem)] items-center gap-12 py-10 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] lg:py-16">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-myanglow-sage bg-white/75 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-myanglow-forest shadow-sm backdrop-blur">
                <Sparkles size={14} />
                Built for smarter farming
              </div>

              <h1 className="mt-7 text-5xl font-semibold leading-[1.05] tracking-tight text-myanglow-navy sm:text-6xl lg:text-7xl">
                From field data to
                <span className="mt-2 block text-myanglow-forest">better harvests.</span>
              </h1>

              <p className="mt-7 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
                One intelligent workspace that combines satellite monitoring, crop recommendations,
                disease detection, market calculations, and practical AI guidance for farmers.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/dashboard"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-myanglow-forest px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-myanglow-forest/20 transition hover:-translate-y-0.5 hover:bg-myanglow-medium"
                >
                  Explore the dashboard 
                </Link>
                <a
                  href="#capabilities"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl border border-myanglow-sage bg-white/85 px-6 py-3.5 text-sm font-semibold text-myanglow-navy transition hover:bg-myanglow-sage/35"
                >
                  See how it works <ChevronDown size={17} />
                </a>
              </div>

              <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-slate-600">
                {['Farmer focused', 'Data informed', 'Mobile ready'].map((item) => (
                  <span key={item} className="inline-flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-myanglow-medium" /> {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-2xl lg:mx-0">
              <div className="absolute -inset-5 rounded-[2.5rem] bg-myanglow-lime/15 blur-2xl" />
              <div className="relative rounded-[2rem] border border-white/90 bg-white/80 p-4 shadow-[0_35px_90px_rgba(12,46,61,0.14)] backdrop-blur-xl sm:p-6">
                <div className="flex items-center justify-between border-b border-myanglow-sage/60 pb-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-myanglow-medium">Field intelligence</p>
                    <h2 className="mt-2 text-xl font-semibold text-myanglow-navy">Farm overview</h2>
                  </div>
                  <span className="inline-flex items-center gap-2 rounded-full bg-myanglow-sage/50 px-3 py-1.5 text-xs font-semibold text-myanglow-darkGreen">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-myanglow-brightLime" /> Active
                  </span>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  {signals.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="rounded-2xl border border-myanglow-sage/70 bg-white p-4 shadow-sm">
                      <div className="flex items-center justify-between text-myanglow-forest">
                        <Icon size={18} />
                        <span className="text-[0.65rem] font-semibold uppercase tracking-wider text-slate-400">Insight</span>
                      </div>
                      <p className="mt-5 text-2xl font-semibold text-myanglow-navy">{value}</p>
                      <p className="mt-1 text-xs text-slate-500">{label}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-[1.25fr_0.75fr]">
                  <div className="overflow-hidden rounded-2xl border border-myanglow-sage/70 bg-gradient-to-br from-myanglow-sage/60 to-white p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-myanglow-medium">Vegetation trend</p>
                        <p className="mt-2 text-sm text-slate-600">Healthy growth over six months</p>
                      </div>
                      <Radar size={24} className="text-myanglow-forest" />
                    </div>
                    <div className="mt-7 flex h-24 items-end gap-2">
                      {[38, 47, 43, 61, 72, 84, 78, 92].map((height, index) => (
                        <div key={index} className="flex-1 rounded-t-md bg-myanglow-forest/80" style={{ height: `${height}%` }} />
                      ))}
                    </div>
                  </div>

                  <div className="rounded-2xl bg-myanglow-navy p-5 text-white">
                    <Sprout size={25} className="text-myanglow-brightLime" />
                    <p className="mt-7 text-xs uppercase tracking-[0.2em] text-myanglow-grayGreen">Recommended</p>
                    <p className="mt-2 text-3xl font-semibold">Rice</p>
                    <p className="mt-2 text-sm text-myanglow-sage">94% field match</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="capabilities" className="relative bg-white/80 py-20 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-medium">One connected platform</p>
            <h2 className="mt-4 text-3xl font-semibold leading-tight text-myanglow-navy sm:text-4xl">Everything needed to understand the field and act faster.</h2>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {capabilities.map(({ icon: Icon, title, description }, index) => (
              <article key={title} className="group rounded-[1.6rem] border border-myanglow-sage/80 bg-white p-6 shadow-[0_14px_40px_rgba(12,46,61,0.06)] transition hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(12,46,61,0.1)]">
                <div className="flex items-center justify-between">
                  <span className="grid h-12 w-12 place-items-center rounded-2xl bg-myanglow-sage/45 text-myanglow-forest transition group-hover:bg-myanglow-forest group-hover:text-white">
                    <Icon size={22} />
                  </span>
                  <span className="text-xs font-semibold text-myanglow-grayGreen">0{index + 1}</span>
                </div>
                <h3 className="mt-6 text-lg font-semibold text-myanglow-navy">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="impact" className="py-20 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="overflow-hidden rounded-[2rem] bg-myanglow-navy px-6 py-10 text-white shadow-[0_30px_80px_rgba(12,46,61,0.2)] sm:px-10 lg:flex lg:items-center lg:justify-between lg:px-14 lg:py-14">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-brightLime">Ready to explore</p>
              <h2 className="mt-4 text-3xl font-semibold leading-tight sm:text-4xl">Make every farming decision count.</h2>
              <p className="mt-4 max-w-xl leading-7 text-myanglow-sage">Explore the complete prototype and see how field signals become useful, farmer-friendly actions.</p>
            </div>
            <Link to="/dashboard" className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-myanglow-brightLime px-6 py-3.5 text-sm font-semibold text-myanglow-navy transition hover:-translate-y-0.5 lg:mt-0">
              Launch dashboard
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}

export default LandingPage
