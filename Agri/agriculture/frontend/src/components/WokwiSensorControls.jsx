import {
  Activity,
  CloudSun,
  ExternalLink,
  Radio,
  Send,
  SlidersHorizontal,
  Thermometer,
  Wifi,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext.jsx'

const WOKWI_PROJECT_URL = 'https://wokwi.com/projects/470253321537782785'
const MIN_CONDITION_SCORE = 5

function rangePenalty(value, minimum, maximum, weight, minimumPenalty = 0) {
  if (value >= minimum && value <= maximum) return 0
  const distance = value < minimum ? minimum - value : value - maximum
  return Math.min(
    100,
    Math.max(
      minimumPenalty,
      (distance / Math.max(maximum - minimum, 0.001)) * weight,
    ),
  )
}

function analyzeReading(reading) {
  const risks = [
    {
      status: reading.soilMoisture < 40 ? 'needsWater' : 'excessWater',
      recommendation: reading.soilMoisture < 40 ? 'needsWater' : 'excessWater',
      penalty: rangePenalty(reading.soilMoisture, 40, 80, 100, 55),
    },
    {
      status: reading.soilPH < 5.5 || reading.soilPH > 7.5 ? 'poorPh' : 'healthy',
      recommendation: reading.soilPH < 5.5 || reading.soilPH > 7.5 ? 'poorPh' : 'healthy',
      penalty: rangePenalty(reading.soilPH, 5.5, 7.5, 100, 55),
    },
    {
      status: reading.temperature < 18
        ? 'coldStress'
        : reading.temperature > 35 ? 'heatStress' : 'healthy',
      recommendation: reading.temperature < 18
        ? 'coldStress'
        : reading.temperature > 35 ? 'heatStress' : 'healthy',
      penalty: rangePenalty(reading.temperature, 18, 35, 100),
    },
    {
      status: reading.lightIntensity < 60 ? 'lowLight' : 'healthy',
      recommendation: reading.lightIntensity < 60 ? 'lowLight' : 'healthy',
      penalty: rangePenalty(reading.lightIntensity, 60, 100, 100),
    },
    {
      status: 'healthy',
      recommendation: 'healthy',
      penalty: rangePenalty(reading.humidity, 40, 85, 25),
    },
  ]

  const healthScore = Math.max(
    MIN_CONDITION_SCORE,
    Math.min(100, 100 - risks.reduce((total, risk) => total + risk.penalty, 0)),
  )
  const worstRisk = risks.reduce(
    (worst, risk) => risk.penalty > worst.penalty ? risk : worst,
    risks[0],
  )
  const hasRisk = worstRisk.penalty > 0

  return {
    status: hasRisk ? worstRisk.status : 'healthy',
    recommendation: hasRisk ? worstRisk.recommendation : 'healthy',
    healthScore: Math.round(healthScore * 10) / 10,
    pumpActive: reading.soilMoisture < 40,
  }
}

function SliderControl({
  label,
  value,
  min,
  max,
  step,
  unit,
  color,
  secondaryValue,
  onChange,
}) {
  const progress = ((value - min) / (max - min)) * 100

  return (
    <label className="block rounded-xl border border-slate-200 bg-slate-50/70 p-3.5">
      <span className="mb-2 flex items-center justify-between gap-3">
        <span className="text-xs font-semibold text-slate-600">{label}</span>
        <span className="text-sm font-bold text-slate-800">
          {Number(value).toFixed(step < 1 ? 1 : 0)}
          <span className="ml-0.5 text-xs font-medium text-slate-400">{unit}</span>
        </span>
      </span>
      <input
        type="range"
        className="iot-range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        style={{
          '--range-color': color,
          background: `linear-gradient(90deg, ${color} 0%, ${color} ${progress}%, #E2E8F0 ${progress}%, #E2E8F0 100%)`,
        }}
        aria-label={label}
      />
      <span className="mt-1.5 block text-[10px] font-medium text-slate-400">
        {secondaryValue}
      </span>
    </label>
  )
}

export default function WokwiSensorControls({
  draft,
  networkMode,
  onChange,
  onNetworkModeChange,
  onApply,
  isApplying,
  syncStatus,
}) {
  const { t } = useLanguage()
  const result = analyzeReading(draft)
  const statusTone = result.healthScore < 50
    ? 'border-red-200 bg-red-50 text-red-700'
    : result.status === 'healthy'
    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
    : result.pumpActive
      ? 'border-blue-200 bg-blue-50 text-blue-700'
      : 'border-amber-200 bg-amber-50 text-amber-700'
  const scoreColor = result.healthScore >= 80
    ? '#16A34A'
    : result.healthScore >= 60
      ? '#D97706'
      : '#DC2626'

  const soilAdc = Math.round((draft.soilMoisture / 100) * 4095)
  const phAdc = Math.round(((draft.soilPH - 3) / 7) * 4095)
  const lightAdc = Math.round((draft.lightIntensity / 100) * 4095)

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-4 py-4 lg:px-6">
        <div className="flex items-start gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
            <SlidersHorizontal size={19} />
          </span>
          <div>
            <h2 className="m-0 text-base font-bold text-slate-800">{t('iot.controlsTitle')}</h2>
            <p className="mt-0.5 text-xs text-slate-500">{t('iot.controlsSubtitle')}</p>
          </div>
        </div>
        <a
          href={WOKWI_PROJECT_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 no-underline transition hover:border-emerald-300 hover:text-emerald-700"
        >
          {t('iot.openWokwi')}
          <ExternalLink size={13} />
        </a>
      </div>

      <div className="grid gap-5 p-4 lg:grid-cols-[minmax(0,1fr)_280px] lg:p-6">
        <div className="min-w-0">
          <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
            <Activity size={14} />
            {t('iot.potentiometers')}
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <SliderControl
              label={t('iot.soilMoisture')}
              value={draft.soilMoisture}
              min={0}
              max={100}
              step={1}
              unit="%"
              color="#2E7D32"
              secondaryValue={`${soilAdc} / 4095 ADC`}
              onChange={(value) => onChange('soilMoisture', value)}
            />
            <SliderControl
              label={t('iot.soilPh')}
              value={draft.soilPH}
              min={3}
              max={10}
              step={0.1}
              unit=" pH"
              color="#8E44AD"
              secondaryValue={`${phAdc} / 4095 ADC · ${t('iot.demoEstimate')}`}
              onChange={(value) => onChange('soilPH', value)}
            />
            <SliderControl
              label={t('iot.light')}
              value={draft.lightIntensity}
              min={0}
              max={100}
              step={1}
              unit="%"
              color="#F39C12"
              secondaryValue={`${lightAdc} / 4095 ADC`}
              onChange={(value) => onChange('lightIntensity', value)}
            />
          </div>

          <div className="mb-3 mt-5 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
            <CloudSun size={14} />
            DHT22
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <SliderControl
              label={t('iot.temperature')}
              value={draft.temperature}
              min={-10}
              max={50}
              step={1}
              unit="°C"
              color="#E11D48"
              secondaryValue="DHT22"
              onChange={(value) => onChange('temperature', value)}
            />
            <SliderControl
              label={t('iot.humidity')}
              value={draft.humidity}
              min={0}
              max={100}
              step={1}
              unit="%"
              color="#0EA5E9"
              secondaryValue="DHT22"
              onChange={(value) => onChange('humidity', value)}
            />
          </div>
        </div>

        <div className="flex min-w-0 flex-col gap-4 rounded-xl border border-slate-200 bg-slate-50/70 p-4">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
              <Radio size={14} />
              {t('iot.transmission')}
            </div>
            <div className="grid grid-cols-2 rounded-xl bg-slate-200/70 p-1" role="group" aria-label={t('iot.transmission')}>
              <button
                type="button"
                onClick={() => onNetworkModeChange('lorawan')}
                className={`flex items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-bold transition ${
                  networkMode === 'lorawan'
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'bg-transparent text-slate-500'
                }`}
                aria-pressed={networkMode === 'lorawan'}
              >
                <Radio size={13} />
                LoRaWAN
              </button>
              <button
                type="button"
                onClick={() => onNetworkModeChange('4g')}
                className={`flex items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-bold transition ${
                  networkMode === '4g'
                    ? 'bg-white text-blue-700 shadow-sm'
                    : 'bg-transparent text-slate-500'
                }`}
                aria-pressed={networkMode === '4g'}
              >
                <Wifi size={13} />
                4G
              </button>
            </div>
          </div>

          <div className={`rounded-xl border p-3 ${statusTone}`}>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold">{t('iot.cropHealth')}</span>
              <span className="text-lg font-extrabold">{result.healthScore}%</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/70">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{ width: `${result.healthScore}%`, backgroundColor: scoreColor }}
              />
            </div>
            <p className="mb-0 mt-2 text-xs font-bold">{t(`iot.status.${result.status}`)}</p>
            <p className="mb-0 mt-1 text-[11px] leading-relaxed opacity-80">
              {t(`iot.recommendation.${result.recommendation}`)}
            </p>
          </div>

          <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2.5">
            <span className="flex items-center gap-2 text-xs font-semibold text-slate-600">
              <Thermometer size={14} />
              {t('iot.virtualPump')}
            </span>
            <span className={`rounded-full px-2 py-1 text-[10px] font-extrabold ${
              result.pumpActive
                ? 'bg-blue-100 text-blue-700'
                : 'bg-slate-100 text-slate-500'
            }`}>
              {result.pumpActive ? t('iot.on') : t('iot.off')}
            </span>
          </div>

          <button
            type="button"
            onClick={onApply}
            disabled={isApplying}
            className="mt-auto inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[#1E5E3A] px-4 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-[#174b2f] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2"
          >
            <Send size={15} />
            {isApplying ? t('iot.applying') : t('iot.applyReading')}
          </button>
          {syncStatus && (
            <p className="m-0 text-center text-[11px] font-medium text-slate-500" role="status">
              {t(`iot.sync.${syncStatus}`)}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
