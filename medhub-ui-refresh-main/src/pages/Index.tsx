import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";

const MetricCard = ({ label, value, delta, deltaType }: { label: string; value: string; delta?: string; deltaType?: "up" | "down" }) => (
  <Card>
    <CardContent className="p-4">
      <p className="text-xs text-secondary-foreground mb-1">{label}</p>
      <p className="text-[28px] font-semibold text-foreground leading-tight">{value}</p>
      {delta && (
        <p className={`text-xs mt-1 ${deltaType === "up" ? "text-success" : "text-danger"}`}>
          {deltaType === "up" ? "↑" : "↓"} {delta}
        </p>
      )}
    </CardContent>
  </Card>
);

const FlashcardFront = () => (
  <Card className="max-w-[780px]">
    <CardContent className="p-5">
      <p className="text-sm italic text-muted-foreground mb-4">
        Clínica Médica › Cardiologia · Erro #12
      </p>
      <p className="text-lg font-medium text-foreground leading-relaxed">
        Paciente de 62 anos, hipertenso, apresenta dor torácica típica com supra de ST em parede inferior. Qual a artéria mais provavelmente acometida?
      </p>
    </CardContent>
  </Card>
);

const FlashcardBack = () => (
  <Card className="max-w-[780px] border-primary/30">
    <CardContent className="p-5 space-y-4">
      <p className="text-base text-foreground leading-relaxed">
        Artéria coronária direita (ACD). O supra de ST em parede inferior (DII, DIII, aVF) indica acometimento da ACD na maioria dos casos.
      </p>
      {/* Regra Mestre */}
      <div className="bg-navy border-l-[3px] border-l-primary rounded-[10px] p-3 px-4">
        <p className="text-xs font-medium text-accent-hint mb-1">Regra Mestre</p>
        <p className="text-sm text-foreground">
          Parede inferior = DII, DIII, aVF → ACD (85% dos casos). Parede anterior = V1-V4 → DA.
        </p>
      </div>
      {/* Armadilha */}
      <div className="bg-[#1A1200] border-l-[3px] border-l-warning rounded-[10px] p-3 px-4">
        <p className="text-xs font-medium text-warning mb-1">Armadilha</p>
        <p className="text-sm text-foreground">
          Em ~15% dos pacientes, a circunflexa é dominante e pode causar IAM inferior. Sempre avaliar V7-V8 para parede posterior.
        </p>
      </div>
    </CardContent>
  </Card>
);

const FSRSButtons = () => (
  <div className="grid grid-cols-4 gap-3 max-w-[780px]">
    <button className="py-2.5 px-3 rounded-xl text-sm font-medium bg-[#1A0A0A] text-danger border border-danger/40 hover:brightness-110 transition-all">
      Novamente
    </button>
    <button className="py-2.5 px-3 rounded-xl text-sm font-medium bg-[#1A1200] text-warning border border-warning/40 hover:brightness-110 transition-all">
      Difícil
    </button>
    <button className="py-2.5 px-3 rounded-xl text-sm font-medium bg-background text-secondary-foreground border border-border-soft hover:brightness-110 transition-all">
      Bom
    </button>
    <button className="py-2.5 px-3 rounded-xl text-sm font-medium bg-[#091A12] text-success border border-success/40 hover:brightness-110 transition-all">
      Fácil
    </button>
  </div>
);

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar simulation */}
      <div className="flex">
        <aside className="w-[220px] min-h-screen bg-secondary border-r border-border p-4 flex flex-col gap-1 shrink-0">
          <div className="flex items-center gap-2 mb-6 px-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <span className="text-primary font-bold text-sm">M</span>
            </div>
            <span className="font-semibold text-foreground text-base">MedHub</span>
          </div>

          {["Dashboard", "Flashcards", "Caderno de Erros", "Resumos"].map((item, i) => (
            <button
              key={item}
              className={`w-full text-left px-3 py-2 rounded-[10px] text-sm transition-all duration-150 ${
                i === 0
                  ? "bg-card text-foreground font-medium"
                  : "text-secondary-foreground hover:bg-card hover:text-foreground"
              }`}
            >
              {item}
            </button>
          ))}

          <Separator className="my-3" />
          <p className="px-3 text-[11px] uppercase tracking-[0.08em] text-muted-foreground mb-1">Configurações</p>
          {["Perfil", "Preferências"].map((item) => (
            <button
              key={item}
              className="w-full text-left px-3 py-2 rounded-[10px] text-sm text-secondary-foreground hover:bg-card hover:text-foreground transition-all duration-150"
            >
              {item}
            </button>
          ))}
        </aside>

        {/* Main content */}
        <main className="flex-1 p-8 space-y-10 animate-fade-in overflow-auto">
          {/* Header */}
          <div>
            <h1 className="text-[32px] font-semibold">Dashboard</h1>
            <p className="text-secondary-foreground text-sm mt-1">Visão geral do seu progresso de estudos</p>
          </div>

          {/* Section: Metric Cards */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Métricas</h2>
            <div className="grid grid-cols-3 gap-4">
              <MetricCard label="Questões respondidas" value="847" delta="12% esta semana" deltaType="up" />
              <MetricCard label="Taxa de acerto" value="72%" delta="3% vs. anterior" deltaType="up" />
              <MetricCard label="Erros pendentes" value="23" delta="5 novos" deltaType="down" />
            </div>
          </section>

          <Separator />

          {/* Section: Buttons */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Botões</h2>
            <div className="flex flex-wrap gap-3 items-center">
              <Button>Primário</Button>
              <Button variant="secondary">Secundário</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destrutivo</Button>
              <Button variant="link">Link</Button>
            </div>
          </section>

          <Separator />

          {/* Section: Inputs */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Campos de entrada</h2>
            <div className="grid grid-cols-2 gap-4 max-w-2xl">
              <div>
                <label className="text-xs text-secondary-foreground mb-1.5 block">Buscar questão</label>
                <Input placeholder="Digite para buscar..." />
              </div>
              <div>
                <label className="text-xs text-secondary-foreground mb-1.5 block">Área de estudo</label>
                <Input placeholder="Ex: Cardiologia" />
              </div>
            </div>
          </section>

          <Separator />

          {/* Section: Badges */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Status badges</h2>
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-success/15 text-success border-success/30">Concluído</Badge>
              <Badge className="bg-warning/15 text-warning border-warning/30">Em revisão</Badge>
              <Badge className="bg-danger/15 text-danger border-danger/30">Urgente</Badge>
              <Badge className="bg-info/15 text-info border-info/30">Informativo</Badge>
              <Badge>Padrão</Badge>
              <Badge variant="outline">Outline</Badge>
            </div>
          </section>

          <Separator />

          {/* Section: Progress bar */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Barra de progresso</h2>
            <div className="max-w-md space-y-3">
              <div className="flex justify-between text-xs text-secondary-foreground mb-1">
                <span>Cardiologia</span>
                <span>14/20 questões</span>
              </div>
              <Progress value={70} className="h-1" />
            </div>
          </section>

          <Separator />

          {/* Section: Card padrão */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Card padrão</h2>
            <Card className="max-w-md">
              <CardHeader>
                <CardTitle className="text-base">Aproveitamento por Disciplina</CardTitle>
                <CardDescription>Dados dos últimos 30 dias</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { area: "Clínica Médica", pct: 78 },
                  { area: "Cirurgia", pct: 65 },
                  { area: "Pediatria", pct: 82 },
                  { area: "GO", pct: 71 },
                ].map((d) => (
                  <div key={d.area}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-secondary-foreground">{d.area}</span>
                      <span className="text-foreground font-medium">{d.pct}%</span>
                    </div>
                    <div className="h-1.5 bg-border rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${d.pct}%` }} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>

          <Separator />

          {/* Section: Flashcard */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Flashcard — Frente</h2>
            <FlashcardFront />
          </section>

          <Separator />

          <section>
            <h2 className="text-lg font-semibold mb-4">Flashcard — Verso</h2>
            <FlashcardBack />
          </section>

          <Separator />

          {/* Section: FSRS Buttons */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Botões FSRS (Rating)</h2>
            <FSRSButtons />
          </section>

          <Separator />

          {/* Section: Expander / Caderno de Erros */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Caderno de Erros (Expander)</h2>
            <div className="space-y-3 max-w-2xl">
              {[
                { n: 12, area: "Clínica Médica", tema: "IAM Inferior" },
                { n: 13, area: "Cirurgia", tema: "Abdome Agudo" },
              ].map((e) => (
                <details
                  key={e.n}
                  className="group bg-card border border-border rounded-lg overflow-hidden hover:border-border-soft transition-colors"
                >
                  <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-foreground flex justify-between items-center">
                    <span>Erro #{e.n} — {e.area} › {e.tema}</span>
                    <span className="text-muted-foreground text-xs group-open:rotate-90 transition-transform">▶</span>
                  </summary>
                  <div className="px-4 pb-4 pt-1 space-y-3">
                    <p className="text-sm text-secondary-foreground">
                      Confundi a artéria responsável pela irrigação da parede inferior do coração.
                    </p>
                    <div className="bg-navy border-l-[3px] border-l-primary rounded-[10px] p-3 px-4">
                      <p className="text-xs font-medium text-accent-hint mb-1">Regra Mestre</p>
                      <p className="text-sm text-foreground">Parede inferior = ACD em 85% dos casos.</p>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </section>

          {/* Color palette reference */}
          <Separator />
          <section className="pb-12">
            <h2 className="text-lg font-semibold mb-4">Paleta de Cores</h2>
            <div className="grid grid-cols-6 gap-3">
              {[
                { name: "Background", cls: "bg-background border" },
                { name: "Secondary", cls: "bg-secondary border" },
                { name: "Surface", cls: "bg-card border" },
                { name: "Elevated", cls: "bg-surface-elevated border" },
                { name: "Navy", cls: "bg-navy" },
                { name: "Accent", cls: "bg-primary" },
                { name: "Accent Soft", cls: "bg-accent-soft" },
                { name: "Accent Hint", cls: "bg-accent-hint" },
                { name: "Success", cls: "bg-success" },
                { name: "Warning", cls: "bg-warning" },
                { name: "Danger", cls: "bg-danger" },
                { name: "Info", cls: "bg-info" },
              ].map((c) => (
                <div key={c.name} className="flex flex-col items-center gap-1.5">
                  <div className={`w-full aspect-square rounded-lg ${c.cls}`} />
                  <span className="text-[10px] text-muted-foreground">{c.name}</span>
                </div>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default Index;
