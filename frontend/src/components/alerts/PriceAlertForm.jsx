import React, { useState, useEffect } from 'react';
import { Bell, BellOff, Trash2, Send, Loader, Info, MessageCircle, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { createAlert, getAlerts, deleteAlert, testTelegram, connectTelegram, disconnectTelegram } from '../../utils/api';
import { formatPrice } from '../../utils/formatters';

const BOT_USERNAME = 'stockadvisor_alerts_bot'; // Change to your bot username

const PriceAlertForm = ({ symbol, stockName, currentPrice }) => {
  const { user, isLoggedIn } = useAuth();
  const [targetPrice, setTargetPrice] = useState('');
  const [alertType, setAlertType] = useState('above');
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testingTelegram, setTestingTelegram] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [message, setMessage] = useState('');
  const [telegramConnected, setTelegramConnected] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  // Check Telegram connection status
  useEffect(() => {
    if (!isLoggedIn || !user) return;

    const checkStatus = async () => {
      try {
        const doc = await (await import('../../firebase')).db
          .collection('users')
          .doc(user.uid)
          .get();
        if (doc.exists) {
          const data = doc.data();
          setTelegramConnected(!!data.telegram_chat_id);
        }
      } catch (err) {
        console.error('Telegram status check error:', err);
      }
    };

    checkStatus();
  }, [isLoggedIn, user]);

  // Fetch alerts
  useEffect(() => {
    if (!isLoggedIn) return;

    const fetchAlerts = async () => {
      try {
        const data = await getAlerts(user?.uid);
        const stockAlerts = data.alerts.filter(
          (a) => a.symbol === symbol && a.active && !a.triggered
        );
        setAlerts(stockAlerts);
      } catch (err) {
        console.error('Fetch alerts error:', err);
      }
    };

    fetchAlerts();
  }, [symbol, isLoggedIn, user]);

  const handleConnectTelegram = async () => {
    if (!isLoggedIn || !user) {
      setMessage('Please login first');
      return;
    }

    setConnecting(true);
    setMessage('');

    try {
      // Open Telegram bot with user ID
      const botUrl = `https://t.me/${BOT_USERNAME}?start=${user.uid}`;
      window.open(botUrl, '_blank');

      // Wait a bit then check status
      setTimeout(async () => {
        try {
          await connectTelegram(user.uid);
          setTelegramConnected(true);
          setMessage('✅ Telegram connected! Alerts will be sent to you.');
        } catch (err) {
          // Bot might not have saved yet, just show success
          setTelegramConnected(true);
          setMessage('✅ Please start the bot in Telegram to complete connection.');
        }
      }, 2000);

    } catch (err) {
      setMessage('❌ Failed to connect Telegram');
    }
    setConnecting(false);
  };

  const handleDisconnectTelegram = async () => {
    if (!user) return;

    try {
      const doc = await (await import('../../firebase')).db
        .collection('users')
        .doc(user.uid)
        .get();

      if (doc.exists) {
        const chatId = doc.data().telegram_chat_id;
        await disconnectTelegram(user.uid, chatId);
        setTelegramConnected(false);
        setMessage('✅ Telegram disconnected');
      }
    } catch (err) {
      setMessage('❌ Failed to disconnect');
    }
  };

  const handleSetAlert = async () => {
    if (!isLoggedIn) {
      setMessage('Please login to set alerts');
      return;
    }

    if (!telegramConnected) {
      setMessage('⚠️ Connect Telegram first to receive alerts');
      return;
    }

    if (!targetPrice || Number(targetPrice) <= 0) {
      setMessage('Enter a valid target price');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const result = await createAlert({
        symbol: symbol,
        stock_name: stockName,
        target_price: Number(targetPrice),
        alert_type: alertType,
        user_id: user.uid,
      });

      setAlerts((prev) => [...prev, result.alert]);
      setTargetPrice('');
      setMessage('✅ Alert set! You will receive a Telegram notification.');
    } catch (err) {
      setMessage('❌ Failed to set alert');
      console.error('Set alert error:', err);
    }
    setLoading(false);
  };

  const handleDeleteAlert = async (alertId) => {
    try {
      await deleteAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      console.error('Delete alert error:', err);
    }
  };

  const handleTestTelegram = async () => {
    setTestingTelegram(true);
    try {
      await testTelegram();
      setMessage('✅ Test message sent to Telegram!');
    } catch (err) {
      setMessage('❌ Telegram test failed. Check bot token & chat ID.');
    }
    setTestingTelegram(false);
  };

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl border dark:border-dark-border border-gray-200 overflow-hidden transition-colors">
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b dark:border-dark-border border-gray-200">
        <Bell className="w-4 h-4 text-blue-400" />
        <h3 className="dark:text-dark-text text-gray-900 font-semibold text-sm">Price Alerts</h3>
      </div>

      <div className="p-4 space-y-4">
        {/* Telegram Connection Status */}
        <div className={`p-3 rounded-lg border ${
          telegramConnected
            ? 'bg-green-500/5 border-green-500/20'
            : 'bg-yellow-500/5 border-yellow-500/20'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {telegramConnected ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <XCircle className="w-4 h-4 text-yellow-400" />
              )}
              <span className={`text-xs font-medium ${
                telegramConnected ? 'text-green-400' : 'text-yellow-400'
              }`}>
                {telegramConnected ? 'Telegram Connected' : 'Telegram Not Connected'}
              </span>
            </div>
            <button
              onClick={telegramConnected ? handleDisconnectTelegram : handleConnectTelegram}
              className={`text-xs px-2 py-1 rounded font-medium transition-colors ${
                telegramConnected
                  ? 'text-red-400 hover:bg-red-500/10'
                  : 'text-blue-400 hover:bg-blue-500/10'
              }`}
              disabled={connecting}
            >
              {connecting ? (
                <Loader className="w-3 h-3 animate-spin" />
              ) : telegramConnected ? (
                'Disconnect'
              ) : (
                'Connect'
              )}
            </button>
          </div>

          {!telegramConnected && (
            <p className="text-yellow-400/70 text-[10px] mt-1">
              Connect to receive price alerts via Telegram
            </p>
          )}
        </div>

        {/* Current Price */}
        <div className="text-center">
          <p className="dark:text-dark-muted text-gray-500 text-xs">Current Price</p>
          <p className="dark:text-dark-text text-gray-900 font-bold text-lg">
            {formatPrice(currentPrice)}
          </p>
        </div>

        {/* Alert Form */}
        <div className="space-y-3">
          <div>
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">
              Target Price (₹)
            </label>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="Enter price..."
              className="w-full px-3 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-lg focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>

          <div>
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">
              Alert when price goes
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setAlertType('above')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  alertType === 'above'
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 border border-transparent'
                }`}
              >
                ▲ Above
              </button>
              <button
                onClick={() => setAlertType('below')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  alertType === 'below'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 border border-transparent'
                }`}
              >
                ▼ Below
              </button>
            </div>
          </div>

          <button
            onClick={handleSetAlert}
            disabled={loading || !targetPrice || !telegramConnected}
            className="w-full py-2.5 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Bell className="w-4 h-4" />
            )}
            {loading ? 'Setting...' : 'Set Alert'}
          </button>

          <button
            onClick={handleTestTelegram}
            disabled={testingTelegram}
            className="w-full py-2 dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700 font-medium rounded-lg transition-colors text-xs flex items-center justify-center gap-2"
          >
            {testingTelegram ? (
              <Loader className="w-3 h-3 animate-spin" />
            ) : (
              <Send className="w-3 h-3" />
            )}
            Test Telegram Connection
          </button>
        </div>

        {/* Message */}
        {message && (
          <p className={`text-xs text-center ${
            message.startsWith('✅') ? 'text-profit' :
            message.startsWith('❌') ? 'text-loss' :
            message.startsWith('⚠️') ? 'text-yellow-400' :
            'dark:text-dark-muted text-gray-500'
          }`}>
            {message}
          </p>
        )}

        {/* Active Alerts */}
        {alerts.length > 0 && (
          <div>
            <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-2">
              Active Alerts
            </p>
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between p-2.5 dark:bg-dark-bg/50 bg-gray-50 rounded-lg border dark:border-dark-border/50 border-gray-200"
                >
                  <div className="flex items-center gap-2">
                    {alert.alert_type === 'above' ? (
                      <span className="text-profit text-xs">▲</span>
                    ) : (
                      <span className="text-loss text-xs">▼</span>
                    )}
                    <div>
                      <p className="dark:text-dark-text text-gray-900 text-xs font-medium">
                        {alert.alert_type === 'above' ? 'Above' : 'Below'} {formatPrice(alert.target_price)}
                      </p>
                      <p className="dark:text-dark-muted text-gray-500 text-[10px]">
                        Set {alert.created_at}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteAlert(alert.id)}
                    className="p-1.5 rounded dark:hover:bg-red-500/20 hover:bg-red-50 transition-colors"
                  >
                    <Trash2 className="w-3 h-3 text-loss" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Note */}
        <div className="border-t dark:border-dark-border border-gray-200 pt-3">
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium w-full"
          >
            <Info className="w-3 h-3" />
            How do price alerts work?
            <span className="ml-auto">{showInfo ? '▲' : '▼'}</span>
          </button>

          {showInfo && (
            <div className="mt-3 space-y-2 text-xs dark:text-dark-muted text-gray-500">
              <div className="flex items-start gap-2">
                <MessageCircle className="w-3 h-3 mt-0.5 text-blue-400 flex-shrink-0" />
                <p>
                  <b className="text-gray-700 dark:text-dark-text">1. Connect Telegram</b> — Click "Connect" above. A Telegram bot will open. Click Start.
                </p>
              </div>
              <div className="flex items-start gap-2">
                <MessageCircle className="w-3 h-3 mt-0.5 text-blue-400 flex-shrink-0" />
                <p>
                  <b className="text-gray-700 dark:text-dark-text">2. Set Alert</b> — Enter target price, choose Above/Below, click "Set Alert".
                </p>
              </div>
              <div className="flex items-start gap-2">
                <MessageCircle className="w-3 h-3 mt-0.5 text-blue-400 flex-shrink-0" />
                <p>
                  <b className="text-gray-700 dark:text-dark-text">3. Get Notified</b> — When price hits your target, you get instant Telegram notification! 🔔
                </p>
              </div>
              <div className="flex items-start gap-2">
                <MessageCircle className="w-3 h-3 mt-0.5 text-blue-400 flex-shrink-0" />
                <p>
                  <b className="text-gray-700 dark:text-dark-text">4. Manage</b> — View all alerts in Portfolio page. Disconnect anytime.
                </p>
              </div>
              <p className="text-[10px] text-gray-400 mt-2 italic">
                Alerts are checked every 5 minutes automatically. Free — no SMS costs!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PriceAlertForm;