"use client"

import { useEffect, useRef, useState } from "react"
import { getAllStations, loadDemoData, interpolatePW, GridPoint } from "@/lib/api"

interface MapViewProps {
  onStationSelect: (stationId: string) => void
  currentTime: Date
}

interface Station {
  station_id: string
  latitude: number
  longitude: number
  elevation: number
  current_pw: number
  last_update: string
  data_points: number
}

export function MapView({ onStationSelect, currentTime }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const [stations, setStations] = useState<Station[]>([])
  const [gridPoints, setGridPoints] = useState<GridPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load stations and initial interpolation
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Load stations
        const stationsResponse = await getAllStations()
        setStations(stationsResponse.stations)
        
        // Load demo interpolation data
        const demoResponse = await loadDemoData()
        setGridPoints(demoResponse.grid)
        
      } catch (err) {
        console.error("Failed to load initial data:", err)
        setError("Failed to load map data")
      } finally {
        setLoading(false)
      }
    }

    loadInitialData()
  }, [])

  // Update interpolation when time changes
  useEffect(() => {
    const updateInterpolation = async () => {
      try {
        const timestamp = currentTime.toISOString()
        console.log(`Updating interpolation for time: ${timestamp}`)
        
        // Use the demo data endpoint for consistent results
        const response = await loadDemoData()
        setGridPoints(response.grid)
        
        console.log(`Updated with ${response.grid.length} grid points`)
      } catch (err) {
        console.error("Failed to update interpolation:", err)
        // Keep existing grid points on error
      }
    }

    if (stations.length > 0 && gridPoints.length === 0) {
      // Only update if we don't have data yet, to avoid constant reloading
      updateInterpolation()
    }
  }, [currentTime, stations.length, gridPoints.length])

  if (loading) {
    return (
      <div className="relative w-full h-full bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 rounded-lg overflow-hidden flex items-center justify-center">
        <div className="text-center bg-white/90 backdrop-blur-md rounded-lg p-6 shadow-xl">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
          <p className="text-sm text-gray-700 font-medium">Loading GNSS station data...</p>
          <p className="text-xs text-gray-500 mt-1">Initializing precipitation map</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="relative w-full h-full bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 rounded-lg overflow-hidden flex items-center justify-center">
        <div className="text-center bg-white/90 backdrop-blur-md rounded-lg p-6 shadow-xl">
          <div className="text-red-600 mb-3">⚠️</div>
          <p className="text-sm text-red-600 font-medium mb-3">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs hover:bg-blue-700 transition-colors"
          >
            Retry Loading
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full bg-muted rounded-lg overflow-hidden">
      {/* Map background */}
      <div ref={mapRef} className="w-full h-full bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 relative">
        {/* Interpolated PW heatmap - Dense grid for smooth interpolation */}
        <div className="absolute inset-0 opacity-70">
          {/* Generate a dense grid of interpolated points */}
          {Array.from({ length: 50 }, (_, i) => 
            Array.from({ length: 50 }, (_, j) => {
              const gridX = (i / 49) * 100 // 0 to 100%
              const gridY = (j / 49) * 100 // 0 to 100%
              
              // Convert screen coordinates back to lat/lon for interpolation
              const bounds = stations.length > 0 ? {
                latMin: Math.min(...stations.map(s => s.latitude)) - 1.0,
                latMax: Math.max(...stations.map(s => s.latitude)) + 1.0,
                lonMin: Math.min(...stations.map(s => s.longitude)) - 1.0,
                lonMax: Math.max(...stations.map(s => s.longitude)) + 1.0,
              } : { latMin: 35, latMax: 45, lonMin: -80, lonMax: -70 }
              
              const pointLat = bounds.latMax - (gridY / 100) * (bounds.latMax - bounds.latMin)
              const pointLon = bounds.lonMin + (gridX / 100) * (bounds.lonMax - bounds.lonMin)
              
              // Interpolate PW value using Inverse Distance Weighting from stations
              let totalWeight = 0
              let weightedSum = 0
              const minDistance = 0.01 // Prevent division by zero
              
              stations.forEach(station => {
                const distance = Math.sqrt(
                  Math.pow(pointLat - station.latitude, 2) + 
                  Math.pow(pointLon - station.longitude, 2)
                )
                const weight = 1 / Math.max(distance, minDistance)
                totalWeight += weight
                weightedSum += weight * (station.current_pw || 15) // Default PW if missing
              })
              
              const interpolatedPW = totalWeight > 0 ? weightedSum / totalWeight : 15
              
              // Add some noise for realistic variation
              const noise = (Math.random() - 0.5) * 2 // ±1mm variation
              const pwValue = Math.max(0, interpolatedPW + noise)
              
              // Color mapping for precipitation
              let bgColor = '#3b82f6' // Blue
              let opacity = 0.3
              
              if (pwValue > 30) {
                bgColor = '#ef4444' // Red
                opacity = 0.8
              } else if (pwValue > 25) {
                bgColor = '#f97316' // Orange  
                opacity = 0.7
              } else if (pwValue > 20) {
                bgColor = '#eab308' // Yellow
                opacity = 0.6
              } else if (pwValue > 15) {
                bgColor = '#22c55e' // Green
                opacity = 0.5
              } else if (pwValue > 10) {
                bgColor = '#06b6d4' // Cyan
                opacity = 0.4
              }
              
              // Create smooth gradient effect with larger overlapping circles
              const size = Math.max(12, Math.min(24, 12 + (pwValue / 3)))
              
              return (
                <div
                  key={`${i}-${j}`}
                  className="absolute rounded-full transition-all duration-500 hover:scale-110 hover:z-10"
                  style={{
                    left: `${gridX}%`,
                    top: `${gridY}%`,
                    width: `${size}px`,
                    height: `${size}px`,
                    backgroundColor: bgColor,
                    opacity: opacity,
                    filter: 'blur(3px)', // More blur for smoother appearance
                    transform: 'translate(-50%, -50%)',
                    mixBlendMode: 'multiply', // Blend overlapping areas
                  }}
                  title={`Interpolated PW: ${pwValue.toFixed(1)}mm`}
                />
              )
            })
          ).flat()}
          
          {/* Additional API-based grid points if available */}
          {gridPoints.slice(0, 100).map((point, index) => {
            const bounds = stations.length > 0 ? {
              latMin: Math.min(...stations.map(s => s.latitude)) - 1.0,
              latMax: Math.max(...stations.map(s => s.latitude)) + 1.0,
              lonMin: Math.min(...stations.map(s => s.longitude)) - 1.0,
              lonMax: Math.max(...stations.map(s => s.longitude)) + 1.0,
            } : { latMin: 35, latMax: 45, lonMin: -80, lonMax: -70 }
            
            const x = ((point.longitude - bounds.lonMin) / (bounds.lonMax - bounds.lonMin)) * 100
            const y = ((bounds.latMax - point.latitude) / (bounds.latMax - bounds.latMin)) * 100
            
            if (x < 0 || x > 100 || y < 0 || y > 100) return null
            
            const pwValue = point.pw_value || 0
            let bgColor = '#3b82f6'
            
            if (pwValue > 30) bgColor = '#ef4444'
            else if (pwValue > 25) bgColor = '#f97316'
            else if (pwValue > 20) bgColor = '#eab308'
            else if (pwValue > 15) bgColor = '#22c55e'
            else if (pwValue > 10) bgColor = '#06b6d4'
            
            return (
              <div
                key={`api-${index}`}
                className="absolute rounded-full transition-all duration-300 hover:scale-125 hover:z-20"
                style={{
                  left: `${x}%`,
                  top: `${y}%`,
                  width: '8px',
                  height: '8px',
                  backgroundColor: bgColor,
                  opacity: 0.9,
                  filter: 'blur(1px)',
                  transform: 'translate(-50%, -50%)',
                  boxShadow: `0 0 8px ${bgColor}`,
                }}
                title={`API PW: ${pwValue.toFixed(1)}mm ± ${(point.uncertainty || 0).toFixed(1)}mm`}
              />
            )
          })}
        </div>

        {/* GNSS stations */}
        {stations.map((station) => {
          // Use actual coordinate bounds from the demo data
          const bounds = stations.length > 0 ? {
            latMin: Math.min(...stations.map(s => s.latitude)) - 1.0,
            latMax: Math.max(...stations.map(s => s.latitude)) + 1.0,
            lonMin: Math.min(...stations.map(s => s.longitude)) - 1.0,
            lonMax: Math.max(...stations.map(s => s.longitude)) + 1.0,
          } : { latMin: 35, latMax: 45, lonMin: -80, lonMax: -70 }
          
          // Convert lat/lon to screen coordinates
          const x = ((station.longitude - bounds.lonMin) / (bounds.lonMax - bounds.lonMin)) * 100
          const y = ((bounds.latMax - station.latitude) / (bounds.latMax - bounds.latMin)) * 100
          
          // Ensure stations stay within visible bounds and don't overlap with UI elements
          const safeX = Math.max(10, Math.min(90, x))
          const safeY = Math.max(15, Math.min(85, y))
          
          // Color code stations based on PW level
          const pwValue = station.current_pw || 0
          let stationColor = 'border-blue-600 bg-blue-100'
          if (pwValue > 30) stationColor = 'border-red-600 bg-red-100'
          else if (pwValue > 25) stationColor = 'border-orange-600 bg-orange-100'
          else if (pwValue > 20) stationColor = 'border-yellow-600 bg-yellow-100'
          else if (pwValue > 15) stationColor = 'border-green-600 bg-green-100'
          
          return (
            <button
              key={station.station_id}
              className={`absolute w-7 h-7 bg-white border-2 ${stationColor} rounded-full shadow-lg hover:scale-110 hover:shadow-xl transition-all duration-200 cursor-pointer z-30 flex items-center justify-center`}
              style={{
                left: `${safeX}%`,
                top: `${safeY}%`,
                transform: 'translate(-50%, -50%)',
              }}
              onClick={() => onStationSelect(station.station_id)}
              title={`${station.station_id}: ${pwValue.toFixed(1)}mm PW (${station.data_points} measurements)`}
            >
              <div className={`w-3 h-3 rounded-full ${stationColor.includes('blue') ? 'bg-blue-600' : 
                stationColor.includes('red') ? 'bg-red-600' :
                stationColor.includes('orange') ? 'bg-orange-600' :
                stationColor.includes('yellow') ? 'bg-yellow-600' : 'bg-green-600'}`}>
              </div>
            </button>
          )
        })}

        {/* Enhanced Map controls overlay */}
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-md rounded-xl p-4 space-y-3 shadow-xl border border-gray-200 z-40">
          <div className="text-sm font-bold text-gray-800">PW Levels (mm)</div>
          <div className="space-y-2">
            <div className="flex items-center space-x-3 text-xs">
              <div className="w-4 h-4 bg-blue-400 rounded-full shadow-sm"></div>
              <span className="text-gray-700 font-medium">0-10 (Dry)</span>
            </div>
            <div className="flex items-center space-x-3 text-xs">
              <div className="w-4 h-4 bg-green-400 rounded-full shadow-sm"></div>
              <span className="text-gray-700 font-medium">10-20 (Low)</span>
            </div>
            <div className="flex items-center space-x-3 text-xs">
              <div className="w-4 h-4 bg-yellow-400 rounded-full shadow-sm"></div>
              <span className="text-gray-700 font-medium">20-30 (Moderate)</span>
            </div>
            <div className="flex items-center space-x-3 text-xs">
              <div className="w-4 h-4 bg-orange-400 rounded-full shadow-sm"></div>
              <span className="text-gray-700 font-medium">30-40 (High)</span>
            </div>
            <div className="flex items-center space-x-3 text-xs">
              <div className="w-4 h-4 bg-red-500 rounded-full shadow-sm"></div>
              <span className="text-gray-700 font-medium">40+ (Very High)</span>
            </div>
          </div>
          <div className="pt-2 border-t border-gray-200">
            <div className="flex items-center space-x-2 text-xs text-gray-600">
              <div className="w-3 h-3 bg-white border-2 border-blue-600 rounded-full"></div>
              <span>GNSS Stations</span>
            </div>
          </div>
        </div>

        {/* Interactive instructions overlay */}
        <div className="absolute bottom-4 left-4">
          <div className="bg-gray-900/90 backdrop-blur-md rounded-lg p-3 text-center shadow-xl border border-gray-700 z-40">
            <p className="text-sm font-medium text-white">Interactive PW Map</p>
            <p className="text-xs text-gray-300 mt-1">Click stations to view detailed data</p>
          </div>
        </div>
      </div>
    </div>
  )
}
