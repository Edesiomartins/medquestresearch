export default function DashboardHome() {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* CARD 1 */}
        <div className="
          p-6 rounded-2xl
          bg-[rgba(255,255,255,0.7)]
          backdrop-blur-xl
          shadow-[var(--shadow-md)]
          border border-[var(--color-border)]
        ">
          <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-2">
            Bem-vindo ao MedQuestResearch
          </h2>
          <p className="text-[var(--color-text-light)] leading-relaxed">
            Aqui você pode analisar artigos, gerar relatórios críticos,
            organizar estudos e acompanhar suas análises realizadas.
          </p>
        </div>
  
        {/* CARD 2 */}
        <div className="
          p-6 rounded-2xl
          bg-[rgba(255,255,255,0.7)]
          backdrop-blur-xl
          shadow-[var(--shadow-md)]
          border border-[var(--color-border)]
        ">
          <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-2">
            Últimas Análises
          </h2>
          <p className="text-[var(--color-text-light)]">Nenhuma análise recente.</p>
        </div>
  
        {/* CARD 3 */}
        <div className="
          p-6 rounded-2xl
          bg-[rgba(255,255,255,0.7)]
          backdrop-blur-xl
          shadow-[var(--shadow-md)]
          border border-[var(--color-border)]
        ">
          <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-2">
            Próximos Passos
          </h2>
          <ul className="list-disc pl-5 text-[var(--color-text-light)]">
            <li>Enviar um novo artigo</li>
            <li>Executar análise IA</li>
            <li>Visualizar relatórios</li>
          </ul>
        </div>
        
      </div>
    );
  }
  