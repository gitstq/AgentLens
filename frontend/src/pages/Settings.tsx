import { useState } from 'react'
import { Save, Database, DollarSign, Bell } from 'lucide-react'

export default function Settings() {
  const [saved, setSaved] = useState(false)
  const [settings, setSettings] = useState({
    defaultPriceInput: 0.01,
    defaultPriceOutput: 0.03,
    autoTrack: true,
    notifications: true,
  })

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">设置</h2>

      <div className="max-w-2xl space-y-6">
        {/* Pricing Settings */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <DollarSign className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">成本计算</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                默认输入价格 ($/1K tokens)
              </label>
              <input
                type="number"
                step="0.001"
                value={settings.defaultPriceInput}
                onChange={(e) => setSettings({ ...settings, defaultPriceInput: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                默认输出价格 ($/1K tokens)
              </label>
              <input
                type="number"
                step="0.001"
                value={settings.defaultPriceOutput}
                onChange={(e) => setSettings({ ...settings, defaultPriceOutput: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* General Settings */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Database className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">通用设置</h3>
          </div>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <span className="text-gray-700">自动追踪新会话</span>
              <input
                type="checkbox"
                checked={settings.autoTrack}
                onChange={(e) => setSettings({ ...settings, autoTrack: e.target.checked })}
                className="w-5 h-5 text-primary-600 rounded"
              />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-gray-700">启用通知</span>
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                className="w-5 h-5 text-primary-600 rounded"
              />
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saved ? '已保存!' : '保存设置'}
          </button>
        </div>
      </div>
    </div>
  )
}
