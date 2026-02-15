import { Sparkles, Activity, Video, ArrowRight, Zap, Shield, Cpu } from 'lucide-react';

function App() {
  const projects = [
    {
      id: 'insurance',
      title: 'AI Health Insurance Underwriter',
      description: 'Intelligent underwriting with RAG-powered risk assessment, automated premium calculation, and KYC verification',
      icon: Activity,
      gradient: 'from-blue-600 to-cyan-600',
      features: ['Document Processing', 'Risk Evaluation', 'Premium Calculation', 'Policy Chatbot'],
      url: 'http://localhost:5173',
      status: 'Production Ready'
    },
    {
      id: 'transcriber',
      title: 'Medical Video Transcriber',
      description: 'Transform patient consultations into intelligent medical records with multilingual AI transcription',
      icon: Video,
      gradient: 'from-purple-600 to-pink-600',
      features: ['Video Processing', 'AI Transcription', 'Prescription Generation', 'Medical Chatbot'],
      url: 'http://localhost:3002',
      status: 'Production Ready'
    }
  ];

  const handleProjectClick = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-slate-800/50 backdrop-blur-xl bg-slate-900/30">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Sparkles className="w-8 h-8 text-blue-500" />
                  <div className="absolute inset-0 blur-xl bg-blue-500/50" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  usecase.ai
                </h1>
              </div>
              <div className="flex items-center gap-6">
                <a href="https://github.com" target="_blank" className="text-slate-400 hover:text-white transition-colors">
                  GitHub
                </a>
                <a href="/docs" className="text-slate-400 hover:text-white transition-colors">
                  Documentation
                </a>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
              <Zap className="w-4 h-4" />
              <span>AI-Powered Healthcare Solutions</span>
            </div>

            <h2 className="text-6xl md:text-7xl font-bold text-white leading-tight">
              Transform Healthcare
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                with AI Technology
              </span>
            </h2>

            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Production-ready AI solutions for insurance underwriting and medical transcription.
              Built with FastAPI, React, and state-of-the-art LLMs.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto pt-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">2</div>
                <div className="text-sm text-slate-400 mt-1">AI Projects</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">100%</div>
                <div className="text-sm text-slate-400 mt-1">Automation</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">Fast</div>
                <div className="text-sm text-slate-400 mt-1">Processing</div>
              </div>
            </div>
          </div>
        </section>

        {/* Projects Grid */}
        <section className="max-w-7xl mx-auto px-6 pb-20">
          <div className="grid md:grid-cols-2 gap-8">
            {projects.map((project) => {
              const Icon = project.icon;
              return (
                <div
                  key={project.id}
                  onClick={() => handleProjectClick(project.url)}
                  className="group relative bg-slate-900/50 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8 hover:border-slate-700 transition-all duration-300 cursor-pointer overflow-hidden"
                >
                  {/* Gradient Overlay on Hover */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${project.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />

                  {/* Content */}
                  <div className="relative z-10 space-y-6">
                    {/* Icon & Status */}
                    <div className="flex items-start justify-between">
                      <div className={`p-4 rounded-xl bg-gradient-to-br ${project.gradient} shadow-lg`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <span className="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium">
                        {project.status}
                      </span>
                    </div>

                    {/* Title & Description */}
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-slate-300 group-hover:bg-clip-text transition-all">
                        {project.title}
                      </h3>
                      <p className="text-slate-400 leading-relaxed">
                        {project.description}
                      </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      {project.features.map((feature, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50"
                        >
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                          <span className="text-sm text-slate-300">{feature}</span>
                        </div>
                      ))}
                    </div>

                    {/* CTA Button */}
                    <button className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white text-slate-900 font-semibold group-hover:bg-gradient-to-r group-hover:from-blue-500 group-hover:to-purple-500 group-hover:text-white transition-all duration-300">
                      <span>Launch Project</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Technology Stack */}
        <section className="max-w-7xl mx-auto px-6 pb-20">
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 text-center">
              Built with Modern Technology
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'FastAPI', icon: Zap },
                { name: 'React', icon: Cpu },
                { name: 'LangGraph', icon: Sparkles },
                { name: 'ChromaDB', icon: Shield }
              ].map((tech) => {
                const TechIcon = tech.icon;
                return (
                  <div key={tech.name} className="flex flex-col items-center gap-3 p-4 rounded-xl bg-slate-800/30 hover:bg-slate-800/50 transition-colors">
                    <TechIcon className="w-8 h-8 text-blue-400" />
                    <span className="text-sm font-medium text-slate-300">{tech.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-800/50 backdrop-blur-xl bg-slate-900/30">
          <div className="max-w-7xl mx-auto px-6 py-8 text-center text-slate-400 text-sm">
            <p>© 2026 usecase.ai - AI-Powered Healthcare Solutions</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
