'use client';

interface StepItem {
  key: string;
  label: string;
}

interface MetaStepperProps {
  steps: StepItem[];
  activeKey: string;
}

export default function MetaStepper({ steps, activeKey }: MetaStepperProps) {
  const activeIndex = steps.findIndex((item) => item.key === activeKey);
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        {steps.map((step, index) => {
          const done = index < activeIndex;
          const active = index === activeIndex;
          return (
            <div
              key={step.key}
              className={`rounded-lg border p-3 text-sm ${
                active ? 'border-blue-500 bg-blue-50 text-blue-900' : done ? 'border-emerald-500 bg-emerald-50 text-emerald-900' : 'border-slate-200 text-slate-500'
              }`}
            >
              <p className="font-semibold">{step.label}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

