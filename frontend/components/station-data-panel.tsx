"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { useEffect, useState } from "react"
import { getStationData, StationTimeSeriesResponse } from "@/lib/api"

interface StationDataPanelProps {
  selectedStation: string | null
}

export function StationDataPanel({ selectedStation }: StationDataPanelProps) {
  const [stationData, setStationData] = useState<StationTimeSeriesResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (selectedStation) {
      const loadStationData = async () => {
        try {
          setLoading(true)
          setError(null)
          const data = await getStationData(selectedStation)
          setStationData(data)
        } catch (err) {
          console.error("Failed to load station data:", err)
          setError("Failed to load station data")
        } finally {
          setLoading(false)
        }
      }

      loadStationData()
    } else {
      setStationData(null)
    }
  }, [selectedStation])

  if (!selectedStation) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Station Data</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            Select a GNSS station on the map to view detailed data
          </p>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Station Data
            <Badge variant="secondary">{selectedStation}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !stationData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Station Data
            <Badge variant="secondary">{selectedStation}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive text-center py-8">
            {error || "No data available"}
          </p>
        </CardContent>
      </Card>
    )
  }

  // Prepare chart data
  const chartData = stationData.time_series.map((point, index) => ({
    time: new Date(point.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: 'UTC'
    }),
    zwd: point.zenith_wet_delay,
    pw: point.precipitable_water,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Station Data
          <Badge variant="secondary">{selectedStation}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Station Info */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Location</div>
            <div className="font-medium">
              {stationData.location.latitude.toFixed(4)}°N, {Math.abs(stationData.location.longitude).toFixed(4)}°W
            </div>
          </div>
          <div>
            <div className="text-muted-foreground">Elevation</div>
            <div className="font-medium">{stationData.elevation.toFixed(1)} m</div>
          </div>
          <div>
            <div className="text-muted-foreground">Current PW</div>
            <div className="font-medium text-primary">{stationData.statistics.pw_mean.toFixed(1)} mm</div>
          </div>
          <div>
            <div className="text-muted-foreground">Status</div>
            <Badge 
              variant={stationData.status === "Active" ? "default" : "secondary"} 
              className={stationData.status === "Active" ? "bg-green-600" : ""}
            >
              {stationData.status}
            </Badge>
          </div>
        </div>

        {/* Enhanced Time Series Chart */}
        <div>
          <h4 className="font-medium mb-3 text-gray-800">Zenith Wet Delay ({stationData.statistics.data_points} points)</h4>
          <div className="h-56 bg-gray-50 rounded-lg p-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
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
                  label={{ value: 'ZWD (m)', angle: -90, position: 'insideLeft' }}
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
                <Line 
                  type="monotone" 
                  dataKey="zwd" 
                  stroke="#3b82f6" 
                  strokeWidth={3} 
                  dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: "#3b82f6", strokeWidth: 2, fill: "white" }}
                />
                <Line 
                  type="monotone" 
                  dataKey="pw" 
                  stroke="#10b981" 
                  strokeWidth={2} 
                  strokeDasharray="5 5"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex justify-center space-x-4 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-0.5 bg-blue-500"></div>
              <span>ZWD (m)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-0.5 bg-green-500 border-dashed"></div>
              <span>PW (mm)</span>
            </div>
          </div>
        </div>

        {/* Enhanced Quick Stats */}
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 text-center border border-blue-200">
            <div className="text-blue-600 font-medium mb-1">Min ZWD</div>
            <div className="font-bold text-blue-800 text-sm">{stationData.statistics.zwd_min.toFixed(3)}m</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 text-center border border-green-200">
            <div className="text-green-600 font-medium mb-1">Max ZWD</div>
            <div className="font-bold text-green-800 text-sm">{stationData.statistics.zwd_max.toFixed(3)}m</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 text-center border border-purple-200">
            <div className="text-purple-600 font-medium mb-1">Avg ZWD</div>
            <div className="font-bold text-purple-800 text-sm">{stationData.statistics.zwd_mean.toFixed(3)}m</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
