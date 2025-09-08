"use client"

import { useState } from "react"
import { loadDemoData } from "@/lib/api"
import { Sidebar } from "@/components/sidebar"
import { MapView } from "@/components/map-view"
import { TimeSeriesSlider } from "@/components/time-series-slider"
import { StationDataPanel } from "@/components/station-data-panel"
import { ErrorValidationPanel } from "@/components/error-validation-panel"
import { ForecastModePanel } from "@/components/forecast-mode-panel"
import { UploadDataPanel } from "@/components/upload-data-panel"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function Dashboard() {
  const [activeView, setActiveView] = useState("dashboard")
  const [selectedStation, setSelectedStation] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="flex h-screen bg-background">
      <Sidebar activeView={activeView} onViewChange={setActiveView} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Enhanced Header */}
        <header className="border-b border-border p-4 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                GNSS Tropospheric PW Interpolator
              </h1>
              <p className="text-gray-600 mt-1">Real-time atmospheric water vapor analysis dashboard</p>
            </div>
            <button 
              onClick={async () => {
                try {
                  setIsLoading(true)
                  await loadDemoData()
                  console.log('Demo data loaded successfully')
                  // Force a refresh by updating the current time slightly
                  setCurrentTime(new Date(Date.now() + 1000))
                } catch (error) {
                  console.error('Failed to load demo data:', error)
                  alert('Failed to load demo data. Please check if the backend is running.')
                } finally {
                  setIsLoading(false)
                }
              }}
              disabled={isLoading}
              className={`px-6 py-2 ${isLoading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white rounded-lg font-medium transition-colors duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed`}
            >
              {isLoading ? (
                <span className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Loading...</span>
                </span>
              ) : (
                'Load Demo Data'
              )}
            </button>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 overflow-auto p-4">
          {activeView === "dashboard" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full">
              {/* Enhanced Map Section - Takes up 2/3 of the width */}
              <div className="lg:col-span-2 space-y-4">
                <Card className="h-96 shadow-lg border-0 bg-white">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span>Interactive Precipitation Map</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="h-full pt-0">
                    <MapView onStationSelect={setSelectedStation} currentTime={currentTime} />
                  </CardContent>
                </Card>

                <Card className="shadow-lg border-0 bg-white">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span>Time Control</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <TimeSeriesSlider currentTime={currentTime} onTimeChange={setCurrentTime} />
                  </CardContent>
                </Card>
              </div>

              {/* Side Panels */}
              <div className="space-y-4">
                <StationDataPanel selectedStation={selectedStation} />
                <ForecastModePanel onForecastUpdate={(forecast) => {
                  console.log('Forecast updated:', forecast)
                  // You could update the map view with forecast data here
                }} />
              </div>
            </div>
          )}

          {activeView === "upload" && <UploadDataPanel />}
          {activeView === "validation" && <ErrorValidationPanel />}

          {activeView === "about" && (
            <div className="space-y-6">
              {/* Hero Section */}
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                <CardHeader>
                  <CardTitle className="text-2xl text-blue-900 flex items-center space-x-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">PW</span>
                    </div>
                    <span>GNSS Tropospheric PW Interpolator</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-blue-800 text-lg leading-relaxed">
                    Advanced atmospheric science dashboard for real-time GNSS tropospheric precipitable water interpolation and analysis. 
                    Built for atmospheric scientists, meteorologists, and researchers studying water vapor dynamics.
                  </p>
                </CardContent>
              </Card>

              {/* Features Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg text-green-700 flex items-center space-x-2">
                      <div className="w-6 h-6 bg-green-600 rounded flex items-center justify-center">
                        <span className="text-white text-xs">🌍</span>
                      </div>
                      <span>Real-time Integration</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">
                      Seamless integration with GNSS station networks for accurate tropospheric measurements. 
                      Process and visualize atmospheric water vapor data in real-time.
                    </p>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg text-purple-700 flex items-center space-x-2">
                      <div className="w-6 h-6 bg-purple-600 rounded flex items-center justify-center">
                        <span className="text-white text-xs">🗺️</span>
                      </div>
                      <span>Interactive Mapping</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">
                      Advanced heatmap visualization with interpolated precipitable water values across regions. 
                      Click stations for detailed time-series analysis.
                    </p>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg text-orange-700 flex items-center space-x-2">
                      <div className="w-6 h-6 bg-orange-600 rounded flex items-center justify-center">
                        <span className="text-white text-xs">📈</span>
                      </div>
                      <span>ML-Powered Forecasting</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">
                      Gaussian Process Regression and LSTM models for temporal forecasting. 
                      Generate predictions with uncertainty quantification up to 48 hours ahead.
                    </p>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg text-red-700 flex items-center space-x-2">
                      <div className="w-6 h-6 bg-red-600 rounded flex items-center justify-center">
                        <span className="text-white text-xs">🔍</span>
                      </div>
                      <span>Quality Validation</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">
                      Advanced validation tools with RMSE/MAE calculations for data quality assurance. 
                      Compare against radiosonde and reanalysis datasets.
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Technical Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl text-gray-800">Technical Specifications</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Data Processing</h4>
                      <ul className="text-sm text-gray-700 space-y-1">
                        <li>• Zenith Wet Delay (ZWD) processing</li>
                        <li>• Spatial interpolation algorithms</li>
                        <li>• Temporal analysis and forecasting</li>
                        <li>• Quality control and outlier detection</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Machine Learning</h4>
                      <ul className="text-sm text-gray-700 space-y-1">
                        <li>• Gaussian Process Regression (GPR)</li>
                        <li>• Long Short-Term Memory (LSTM)</li>
                        <li>• Inverse Distance Weighting (IDW)</li>
                        <li>• Ordinary Kriging interpolation</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Usage Instructions */}
              <Card className="bg-gray-50 border-gray-200">
                <CardHeader>
                  <CardTitle className="text-xl text-gray-800">Getting Started</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                      <div>
                        <p className="font-medium text-gray-800">Load Demo Data</p>
                        <p className="text-sm text-gray-600">Click "Load Demo Data" to visualize sample GNSS measurements</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                      <div>
                        <p className="font-medium text-gray-800">Explore the Map</p>
                        <p className="text-sm text-gray-600">Use time slider to animate data and click stations for details</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                      <div>
                        <p className="font-medium text-gray-800">Upload Your Data</p>
                        <p className="text-sm text-gray-600">Use the Upload Data tab to analyze your own GNSS measurements</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</div>
                      <div>
                        <p className="font-medium text-gray-800">Generate Forecasts</p>
                        <p className="text-sm text-gray-600">Enable forecast mode to predict future atmospheric conditions</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Footer */}
              <Card className="bg-gradient-to-r from-gray-800 to-gray-900 text-white">
                <CardContent className="pt-6">
                  <div className="text-center space-y-2">
                    <p className="text-lg font-semibold">Built for Atmospheric Research</p>
                    <p className="text-sm text-gray-300">
                      Empowering scientists and meteorologists with advanced GNSS tropospheric analysis tools
                    </p>
                    <div className="flex justify-center space-x-4 text-xs text-gray-400 pt-2">
                      <span>Real-time Processing</span>
                      <span>•</span>
                      <span>ML-Powered Forecasting</span>
                      <span>•</span>
                      <span>Research-Grade Accuracy</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
