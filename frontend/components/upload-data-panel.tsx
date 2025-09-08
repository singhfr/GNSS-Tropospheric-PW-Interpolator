"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileText, Database, CheckCircle, AlertCircle } from "lucide-react"
import { useState } from "react"

interface UploadResult {
  success: boolean
  message: string
  recordCount?: number
  stations?: string[]
}

export function UploadDataPanel() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, dataType: string) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setIsUploading(true)
      setError(null)
      setUploadProgress(0)

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/upload-data', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response.ok) {
        const result = await response.json()
        setUploadResults(prev => [...prev, {
          success: true,
          message: `${dataType} uploaded successfully`,
          recordCount: result.record_count,
          stations: result.stations
        }])
        console.log(`${dataType} uploaded successfully:`, result)
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
    } catch (err) {
      console.error('Upload failed:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to upload ${dataType}: ${errorMessage}`)
      setUploadResults(prev => [...prev, {
        success: false,
        message: `${dataType} upload failed: ${errorMessage}`
      }])
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 2000)
    }
  }

  const clearResults = () => {
    setUploadResults([])
    setError(null)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Data Upload</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Upload Progress */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Uploading...</span>
                <span className="text-gray-600">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded border border-red-200 flex items-center space-x-2">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          )}

          {/* File Upload Sections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* GNSS ZWD Data */}
            <Card className="border-2 border-dashed border-gray-200 hover:border-blue-300 transition-colors">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  <span>GNSS ZWD Data</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600">
                  Upload GNSS Zenith Wet Delay measurements from your station network.
                </p>
                <div className="space-y-2">
                  <Label htmlFor="gnss-data" className="text-gray-700 font-medium">
                    CSV File (timestamp, station_id, lat, lon, elevation, zwd)
                  </Label>
                  <div className="flex space-x-2">
                    <Input
                      id="gnss-data"
                      type="file"
                      accept=".csv,.txt"
                      onChange={(e) => handleFileUpload(e, 'GNSS ZWD')}
                      disabled={isUploading}
                      className="text-gray-900 bg-white border-gray-300"
                    />
                    <Button 
                      size="sm" 
                      disabled={isUploading}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      {isUploading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        <Upload className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Validation Data */}
            <Card className="border-2 border-dashed border-gray-200 hover:border-green-300 transition-colors">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-green-600" />
                  <span>Validation Data</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600">
                  Upload reference data for model validation (Radiosonde, ERA5, etc.).
                </p>
                <div className="space-y-2">
                  <Label htmlFor="validation-data" className="text-gray-700 font-medium">
                    CSV File (timestamp, station_id, lat, lon, wet_delay)
                  </Label>
                  <div className="flex space-x-2">
                    <Input
                      id="validation-data"
                      type="file"
                      accept=".csv,.txt,.nc"
                      onChange={(e) => handleFileUpload(e, 'Validation')}
                      disabled={isUploading}
                      className="text-gray-900 bg-white border-gray-300"
                    />
                    <Button 
                      size="sm" 
                      disabled={isUploading}
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      {isUploading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        <Upload className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Upload Results</CardTitle>
                <Button size="sm" variant="outline" onClick={clearResults}>
                  Clear Results
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {uploadResults.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border flex items-start space-x-3 ${
                        result.success
                          ? 'bg-green-50 border-green-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      {result.success ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className={`font-medium ${
                          result.success ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {result.message}
                        </p>
                        {result.success && result.recordCount && (
                          <p className="text-sm text-green-600 mt-1">
                            Processed {result.recordCount} records
                            {result.stations && ` from ${result.stations.length} stations`}
                          </p>
                        )}
                        {result.success && result.stations && (
                          <p className="text-xs text-green-500 mt-1">
                            Stations: {result.stations.join(', ')}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Instructions */}
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-lg text-blue-800">Data Format Requirements</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-blue-700 space-y-2">
              <div>
                <strong>GNSS ZWD Data:</strong> CSV with columns: timestamp, station_id, latitude, longitude, elevation, zenith_wet_delay
              </div>
              <div>
                <strong>Validation Data:</strong> CSV with columns: timestamp, station_id, latitude, longitude, wet_delay_mm
              </div>
              <div>
                <strong>Timestamp Format:</strong> ISO 8601 (e.g., 2024-01-01T12:00:00Z) or YYYY-MM-DD HH:MM:SS
              </div>
              <div>
                <strong>Coordinates:</strong> Decimal degrees (WGS84)
              </div>
              <div>
                <strong>File Size Limit:</strong> 100MB per file
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  )
}
