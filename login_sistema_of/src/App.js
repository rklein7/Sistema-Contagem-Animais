import React, { useState, useEffect } from 'react';
import { Lock, User, LogOut, CheckCircle, XCircle, Activity, TrendingUp, Calendar, BarChart3, Wifi, WifiOff, PawPrint } from 'lucide-react';

function App() {
  const [view, setView] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [loading, setLoading] = useState(false);
  const [showLoadingScreen, setShowLoadingScreen] = useState(false);
  
  const [stats, setStats] = useState({
    total_animals: 0,
    today: 0,
    this_week: 0,
    this_month: 0,
    total_records: 0
  });
  const [recentCounts, setRecentCounts] = useState([]);
  const [devices, setDevices] = useState([]);

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    if (token && view === 'dashboard') {
      loadDashboardData();
      const interval = setInterval(loadDashboardData, 5000); // Atualiza a cada 5 segundos
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, view]);

  const loadDashboardData = async () => {
    try {
      // Carregar estatísticas
      const statsResponse = await fetch(`${API_URL}/counts/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Carregar contagens recentes
      const countsResponse = await fetch(`${API_URL}/counts/today`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (countsResponse.ok) {
        const countsData = await countsResponse.json();
        setRecentCounts(countsData.counts.slice(-10).reverse());
      }

      // Carregar dispositivos
      const devicesResponse = await fetch(`${API_URL}/devices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (devicesResponse.ok) {
        const devicesData = await devicesResponse.json();
        setDevices(devicesData.devices);
      }
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    }
  };

  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        showMessage('Cadastro realizado com sucesso!', 'success');
        setView('login');
        setPassword('');
      } else {
        showMessage(data.message, 'error');
      }
    } catch (error) {
      showMessage('Erro ao conectar com o servidor', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        setShowLoadingScreen(true);
        // Simula tempo de carregamento e depois vai para o dashboard
        setTimeout(() => {
          setView('dashboard');
          setShowLoadingScreen(false);
          setPassword('');
        }, 4000); // 4 segundos de loading (mais lento)
      } else {
        showMessage(data.message, 'error');
      }
    } catch (error) {
      showMessage('Erro ao conectar com o servidor', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    setUsername('');
    setPassword('');
    setView('login');
    setStats({
      total_animals: 0,
      today: 0,
      this_week: 0,
      this_month: 0,
      total_records: 0
    });
    setRecentCounts([]);
    setDevices([]);
    showMessage('Logout realizado com sucesso!', 'success');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (view === 'login') {
      handleLogin(e);
    } else {
      handleRegister(e);
    }
  };

  const formatDateTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('pt-BR');
  };

  const isDeviceActive = (lastSeen) => {
    const lastSeenDate = new Date(lastSeen);
    const now = new Date();
    const diffMinutes = (now - lastSeenDate) / 1000 / 60;
    return diffMinutes < 5; 
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        {message && (
          <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
            messageType === 'success' 
              ? 'bg-green-500 text-white' 
              : 'bg-red-500 text-white'
          }`}>
            {messageType === 'success' ? <CheckCircle size={20} /> : <XCircle size={20} />}
            {message}
          </div>
        )}

        {showLoadingScreen ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-12 border border-white/20 text-center">
              <div className="mb-6">
                <img 
                  src="/8304a59c2bde6884f8878ef060ddcf49.gif" 
                  alt="Loading" 
                  className="w-32 h-32 mx-auto object-contain"
                />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Carregando Dashboard</h2>
              <p className="text-white/70">Preparando seus dados...</p>
              <div className="mt-6">
                <div className="w-48 bg-white/20 rounded-full h-2 mx-auto">
                  <div className="bg-purple-500 h-2 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        ) : view === 'dashboard' ? (
          <div className="space-y-6">
            {/* Header */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-6 flex justify-between items-center border border-white/20">
              <div>
                <h1 className="text-3xl font-bold text-white">Sistema de Contagem de Animais</h1>
                <p className="text-white/80 mt-1">Bem-vindo, <strong>{username}</strong></p>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-500/80 backdrop-blur-sm text-white px-6 py-3 rounded-lg hover:bg-red-600/80 transition font-medium flex items-center gap-2 border border-red-400/30"
              >
                <LogOut size={20} />
                Sair
              </button>
            </div>

            {/* Cards de Estatísticas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm font-medium">Hoje</p>
                    <h3 className="text-3xl font-bold text-purple-300 mt-1">{stats.today}</h3>
                  </div>
                  <div className="bg-purple-500/20 p-3 rounded-full">
                    <Activity className="text-purple-300" size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm font-medium">Esta Semana</p>
                    <h3 className="text-3xl font-bold text-green-300 mt-1">{stats.this_week}</h3>
                  </div>
                  <div className="bg-green-500/20 p-3 rounded-full">
                    <TrendingUp className="text-green-300" size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm font-medium">Este Mês</p>
                    <h3 className="text-3xl font-bold text-purple-300 mt-1">{stats.this_month}</h3>
                  </div>
                  <div className="bg-purple-500/20 p-3 rounded-full">
                    <Calendar className="text-purple-300" size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm font-medium">Total Geral</p>
                    <h3 className="text-3xl font-bold text-orange-300 mt-1">{stats.total_animals}</h3>
                  </div>
                  <div className="bg-orange-500/20 p-3 rounded-full">
                    <BarChart3 className="text-orange-300" size={24} />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Contagens Recentes */}
              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <h2 className="text-xl font-bold text-white mb-4">Contagens Recentes (Hoje)</h2>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {recentCounts.length === 0 ? (
                    <p className="text-white/70 text-center py-8">Nenhuma contagem registrada hoje</p>
                  ) : (
                    recentCounts.map((count) => (
                      <div key={count.id} className="bg-white/5 border border-white/20 rounded-lg p-4 hover:bg-white/10 transition">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-white">
                              {count.count} {count.count === 1 ? 'animal' : 'animais'}
                            </p>
                            <p className="text-sm text-white/70">Tipo: {count.animal_type}</p>
                            <p className="text-xs text-white/60 mt-1">Dispositivo: {count.device_id.substring(0, 8)}</p>
                          </div>
                          <span className="text-xs text-white/60">{formatDateTime(count.timestamp)}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Dispositivos Conectados */}
              <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/20">
                <h2 className="text-xl font-bold text-white mb-4">Dispositivos Raspberry Pi</h2>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {devices.length === 0 ? (
                    <p className="text-white/70 text-center py-8">Nenhum dispositivo registrado</p>
                  ) : (
                    devices.map((device) => (
                      <div key={device.id} className="bg-white/5 border border-white/20 rounded-lg p-4 hover:bg-white/10 transition">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center gap-3">
                            {isDeviceActive(device.last_seen) ? (
                              <Wifi className="text-green-400" size={20} />
                            ) : (
                              <WifiOff className="text-red-400" size={20} />
                            )}
                            <div>
                              <p className="font-semibold text-white">{device.name}</p>
                              <p className="text-sm text-white/70">{device.location}</p>
                              <p className="text-xs text-white/60 mt-1">
                                Último sinal: {formatDateTime(device.last_seen)}
                              </p>
                            </div>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            isDeviceActive(device.last_seen) 
                              ? 'bg-green-500/20 text-green-300 border border-green-400/30' 
                              : 'bg-red-500/20 text-red-300 border border-red-400/30'
                          }`}>
                            {isDeviceActive(device.last_seen) ? 'Ativo' : 'Inativo'}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="w-full max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[80vh]">
              {/* Lado Esquerdo - Formulário */}
              <div className="flex items-center justify-center p-8">
                <div className="w-full max-w-md">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20">
                    <div className="text-center mb-8">
                      <div className="flex items-center justify-center mx-auto mb-4">
                        <img 
                          src="/Vaquinha.png" 
                          alt="Ícone do sistema" 
                          className="w-32 h-32 object-contain"
                        />
                      </div>
                      <h2 className="text-3xl font-bold text-white">
                        {view === 'login' ? 'Bem-vindo de volta!' : 'Crie sua conta'}
                      </h2>
                      <p className="text-white/80 mt-2">Sistema de Contagem de Animais</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <label className="block text-white font-medium mb-2">Usuário</label>
                        <div className="relative">
                          <User className="absolute left-3 top-3 text-white/60" size={20} />
                          <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent text-white placeholder-white/60"
                            placeholder="Digite seu usuário"
                            required
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-white font-medium mb-2">Senha</label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 text-white/60" size={20} />
                          <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent text-white placeholder-white/60"
                            placeholder="Digite sua senha"
                            required
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-purple-500 text-white py-3 rounded-lg hover:bg-purple-600 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                      >
                        {loading ? 'Processando...' : view === 'login' ? 'Entrar' : 'Cadastrar'}
                      </button>
                    </form>

                    <div className="mt-6 text-center">
                      <button
                        onClick={() => {
                          setView(view === 'login' ? 'register' : 'login');
                          setMessage('');
                          setPassword('');
                        }}
                        className="text-white/80 hover:text-white font-medium transition"
                      >
                        {view === 'login' 
                          ? 'Não tem conta? Cadastre-se' 
                          : 'Já tem conta? Faça login'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Lado Direito - Showcase */}
              <div className="flex items-center justify-center p-8">
                <div className="w-full max-w-lg">
                  <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-white mb-4">
                      Sistema Automatizado de Contagem
                    </h1>
                    <p className="text-white/80 text-lg">
                      Monitore e gerencie a contagem de animais com tecnologia avançada
                    </p>
                  </div>

                  {/* Cards de Features */}
                  <div className="space-y-6">
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <div className="flex items-center gap-4">
                        <div className="bg-purple-500/20 p-3 rounded-lg">
                          <Activity className="text-purple-300" size={24} />
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">Monitoramento em Tempo Real</h3>
                          <p className="text-white/70 text-sm">Acompanhe a contagem de animais instantaneamente</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <div className="flex items-center gap-4">
                        <div className="bg-green-500/20 p-3 rounded-lg">
                          <TrendingUp className="text-green-300" size={24} />
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">Relatórios Detalhados</h3>
                          <p className="text-white/70 text-sm">Gere relatórios diários, semanais e mensais</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <div className="flex items-center gap-4">
                        <div className="bg-blue-500/20 p-3 rounded-lg">
                          <Wifi className="text-blue-300" size={24} />
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">Dispositivos Conectados</h3>
                          <p className="text-white/70 text-sm">Gerencie múltiplos sensores Raspberry Pi</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <div className="flex items-center gap-4">
                        <div className="bg-orange-500/20 p-3 rounded-lg">
                          <BarChart3 className="text-orange-300" size={24} />
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">Dashboard Intuitivo</h3>
                          <p className="text-white/70 text-sm">Interface moderna e fácil de usar</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;