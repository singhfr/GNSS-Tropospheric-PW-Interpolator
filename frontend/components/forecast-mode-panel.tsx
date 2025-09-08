"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { TrendingUp, Clock, MapPin } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { useState } from "react"

// Mock forecast data
const mockForecastData = [
  { time: "00:00", observed: 24.1, forecast: null },
  { time: "02:00", observed: 24.7, forecast: null },
  { time: "04:00", observed: 23.4, forecast: null },
  { time: "06:00", observed: 26.2, forecast: null },
  { time: "08:00", observed: 28.4, forecast: null },
  { time: "10:00", observed: 30.6, forecast: null },
  { time: "11:00", observed: 31.2, forecast: null },
  { time: "12:00", observed: null, forecast: 30.8 },
  { time: "13:00", observed: null, forecast: 29.5 },
  { time: "14:00", observed: null, forecast: 28.2 },
  { time: "15:00", observed: null, forecast: 27.1 },
  { time: "16:00", observed: null, forecast: 26.7 },
  { time: "17:00", observed: null, forecast: 25.9 },
  { time: "18:00", observed: null, forecast: 25.1 },
  { time: "19:00", observed: null, forecast: 24.8 },
  { time: "20:00", observed: null, forecast: 24.3 },
  { time: "21:00", observed: null, forecast: 24.0 },
  { time: "22:00", observed: null, forecast: 23.8 },
]

interface ForecastModePanelProps {
  onForecastUpdate?: (forecast: any) => void
}

export function ForecastModePanel({ onForecastUpdate }: ForecastModePanelProps = {}) {
  const [forecastEnabled, setForecastEnabled] = useState(false)
  const [forecastHours, setForecastHours] = useState([12])
  const [confidenceLevel, setConfidenceLevel] = useState([95])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateForecast = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/api/forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          horizon_hours: forecastHours[0],
          model_type: 'lstm',
          confidence_level: confidenceLevel[0] / 100
        })
      })
      
      if (response.ok) {
        const forecast = await response.json()
        onForecastUpdate?.(forecast)
        console.log('Extended forecast generated successfully:', forecast)
        
        // Show success message
        const successMsg = `Generated ${forecast.grid?.length || 0} forecast points for ${forecastHours[0]}h ahead`
        console.log(successMsg)
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
    } catch (err) {
      console.error('Forecast generation failed:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to generate forecast: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleForecast = async (enabled: boolean) => {
    setForecastEnabled(enabled)
    if (enabled) {
      await handleGenerateForecast()
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Forecast Mode</span>
          </span>
          <Badge variant="secondary" className="bg-chart-1">
            {forecastHours[0]}h Ahead
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Forecast Controls */}
        <div className="flex items-center justify-between">
          <Label htmlFor="forecast-toggle" className="text-sm font-medium">
            Enable Extrapolation
          </Label>
          <Switch 
            id="forecast-toggle" 
            checked={forecastEnabled} 
            onCheckedChange={handleToggleForecast}
            disabled={loading}
          />
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-2 rounded border">
            {error}
          </div>
        )}

        {/* Forecast Parameters */}
        {forecastEnabled && (
          <div className="space-y-4 p-3 bg-gray-50 rounded-lg border">
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Forecast Horizon: {forecastHours[0]} hours
              </Label>
              <Slider
                value={forecastHours}
                onValueChange={setForecastHours}
                max={48}
                min={1}
                step={1}
                className="w-full"
              />
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Confidence Level: {confidenceLevel[0]}%
              </Label>
              <Slider
                value={confidenceLevel}
                onValueChange={setConfidenceLevel}
                max={99}
                min={80}
                step={1}
                className="w-full"
              />
            </div>
          </div>
        )}

        {forecastEnabled && (
          <>
            {/* Forecast Chart */}
            <div className="h-48 bg-white rounded-lg border p-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockForecastData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
                  <XAxis 
                    dataKey="time" 
                    fontSize={11} 
                    tick={{ fill: "#6b7280" }}
                    axisLine={{ stroke: "#d1d5db" }}
                    tickLine={{ stroke: "#d1d5db" }}
                  />
                  <YAxis 
                    fontSize={11} 
                    tick={{ fill: "#6b7280" }}
                    axisLine={{ stroke: "#d1d5db" }}
                    tickLine={{ stroke: "#d1d5db" }}
                    label={{ value: 'PW (mm)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e5e7eb",
                      borderRadius: "8px",
                      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    }}
                    labelStyle={{ color: "#374151", fontWeight: "500" }}
                  />
                  <ReferenceLine 
                    x="12:00" 
                    stroke="#9ca3af" 
                    strokeDasharray="2 2" 
                    label={{ value: "Forecast Start", position: "top" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="observed"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: "#3b82f6", strokeWidth: 2, fill: "white" }}
                    name="Observed"
                    connectNulls={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="forecast"
                    stroke="#10b981"
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: "#10b981", strokeWidth: 2, fill: "white" }}
                    name="Forecast"
                    connectNulls={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Forecast Info */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Next Update:</span>
                <span className="font-medium">12:15 UTC</span>
              </div>

              <div className="flex items-center space-x-2 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Coverage:</span>
                <span className="font-medium">Outside GNSS Network</span>
              </div>

              {/* Forecast Stats */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-secondary rounded p-2 text-center">
                  <div className="text-muted-foreground">Confidence</div>
                  <div className="font-bold text-chart-3">87%</div>
                </div>
                <div className="bg-secondary rounded p-2 text-center">
                  <div className="text-muted-foreground">Uncertainty</div>
                  <div className="font-bold text-chart-2">±2.1mm</div>
                </div>
              </div>

              <Button 
                size="sm" 
                className="w-full" 
                onClick={handleGenerateForecast}
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </span>
                ) : (
                  'Generate Extended Forecast'
                )}
              </Button>
            </div>
          </>
        )}

        {!forecastEnabled && (
          <div className="text-center py-8 text-muted-foreground">
            <TrendingUp className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Forecast mode disabled</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
