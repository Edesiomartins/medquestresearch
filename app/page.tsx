export default function HomePage() {
  return (
    <div className="flex flex-col items-center text-center space-y-12">

      {/* HERO PREMIUM REFINADO */}
      <section className="max-w-3xl space-y-6 pt-10">
        {/* ÍCONE DESTAQUE */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center shadow-lg border border-emerald-200">
            <svg
              viewBox="0 0 100 100"
              className="w-12 h-12 text-emerald-600"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M50 20C35 20 25 30 25 45C25 55 32 63 42 65C42 75 48 85 50 85C52 85 58 75 58 65C68 63 75 55 75 45C75 30 65 20 50 20Z"
                fill="currentColor"
              />
              <path
                d="M50 40V60M40 50H60"
                stroke="white"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
          </div>
        </div>

        <h1 className="text-4xl md:text-5xl font-semibold leading-tight text-slate-900">
          IA aplicada à{" "}
          <span className="text-emerald-600">leitura crítica</span>{" "}
          e análise científica.
        </h1>

        <p className="text-slate-600 text-base md:text-lg leading-relaxed">
          O MedQuestResearch auxilia pesquisadores, professores e alunos
          na compreensão profunda de artigos científicos — oferecendo
          explicações didáticas, validação de informações e avaliação
          crítica estruturada.
        </p>

        {/* BOTÕES MAIS BONITOS */}
        <div className="flex justify-center gap-4 pt-3">
          <button className="px-6 py-3 bg-emerald-600 text-white text-sm font-medium rounded-lg shadow-md hover:bg-emerald-700 transition">
            Iniciar análise
          </button>

          <button className="px-6 py-3 text-sm font-medium rounded-lg border border-slate-300 hover:border-slate-400 hover:bg-slate-100 transition bg-white shadow-sm">
            Enviar PDF
          </button>
        </div>
      </section>

      {/* LINHA DIVISÓRIA SUAVE */}
      <div className="w-full max-w-4xl h-px bg-gradient-to-r from-transparent via-slate-300/40 to-transparent"></div>

      {/* GRID DE RECURSOS PREMIUM */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
        {[
          {
            title: "Leitura crítica",
            desc: "Avalie metodologia, validade e qualidade científica de artigos.",
            tag: "Avaliação",
            icon: "📊"
          },
          {
            title: "Explicar conceitos",
            desc: "Transforme conteúdo complexo em explicações claras e didáticas.",
            tag: "Didática",
            icon: "💡"
          },
          {
            title: "Verificação de fatos",
            desc: "Valide afirmações científicas com base em literatura real.",
            tag: "Precisão",
            icon: "✓"
          },
          {
            title: "Perspectiva e síntese",
            desc: "Compare artigos e construa sínteses e insights aprofundados.",
            tag: "Síntese",
            icon: "🔗"
          }
        ].map((f) => (
          <article
            key={f.title}
            className="group p-6 rounded-xl bg-white border border-slate-200 shadow-sm transition hover:shadow-md hover:border-emerald-400/60"
          >
            <div className="flex items-start justify-between mb-3">
              <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                {f.tag}
              </span>
              <span className="text-2xl">{f.icon}</span>
            </div>

            <h2 className="text-lg font-semibold text-slate-900">{f.title}</h2>

            <p className="mt-1 text-sm text-slate-600 leading-relaxed">
              {f.desc}
            </p>

            <p className="mt-4 text-emerald-600 text-xs opacity-0 group-hover:opacity-100 transition">
              Acessar módulo →
            </p>
          </article>
        ))}
      </section>
    </div>
  );
}