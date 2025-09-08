"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Upload, CheckCircle, AlertCircle } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { useState } from "react"
import { uploadValidationData } from "@/lib/api"

// Mock validation results
const mockValidationData = [
  { station: "GNSS001", rmse: 2.1, mae: 1.8, status: "good" },
  { station: "GNSS002", rmse: 3.4, mae: 2.9, status: "warning" },
  { station: "GNSS003", rmse: 1.7, mae: 1.4, status: "good" },
  { station: "GNSS004", rmse: 4.2, mae: 3.8, status: "error" },
  { station: "GNSS005", rmse: 2.8, mae: 2.3, status: "good" },
]

export function ErrorValidationPanel() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, dataType: string) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setIsUploading(true)
      setError(null)
      
      const results = await uploadValidationData(file)
      setUploadResults(results)
      console.log(`${dataType} uploaded successfully:`, results)
    } catch (err) {
      console.error('Upload failed:', err)
      setError(`Failed to upload ${dataType}: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Error Validation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Upload Section */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Upload Reference Data</h3>
            
            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded border border-red-200">
                {error}
              </div>
            )}
            
            {uploadResults && (
              <div className="text-sm text-green-600 bg-green-50 p-3 rounded border border-green-200">
                Validation completed! RMSE: {uploadResults.rmse?.toFixed(2)}, MAE: {uploadResults.mae?.toFixed(2)}
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="radiosonde" className="text-gray-700 font-medium">Radiosonde Data</Label>
                <div className="flex space-x-2">
                  <Input 
                    id="radiosonde" 
                    type="file" 
                    accept=".csv,.txt" 
                    onChange={(e) => handleFileUpload(e, 'Radiosonde')}
                    disabled={isUploading}
                    className="text-gray-900 bg-white border-gray-300"
                  />
                  <Button size="sm" disabled={isUploading} className="bg-blue-600 hover:bg-blue-700 text-white">
                    {isUploading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="era5" className="text-gray-700 font-medium">ERA5 Reanalysis</Label>
                <div className="flex space-x-2">
                  <Input 
                    id="era5" 
                    type="file" 
                    accept=".nc,.grib,.csv" 
                    onChange={(e) => handleFileUpload(e, 'ERA5')}
                    disabled={isUploading}
                    className="text-gray-900 bg-white border-gray-300"
                  />
                  <Button size="sm" disabled={isUploading} className="bg-blue-600 hover:bg-blue-700 text-white">
                    {isUploading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Validation Results */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Validation Results</h3>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                <div className="text-sm text-gray-600">Overall RMSE</div>
                <div className="text-xl font-bold text-blue-600">{uploadResults?.rmse?.toFixed(2) || '2.84'} mm</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                <div className="text-sm text-gray-600">Overall MAE</div>
                <div className="text-xl font-bold text-green-600">{uploadResults?.mae?.toFixed(2) || '2.44'} mm</div>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-center">
                <div className="text-sm text-gray-600">Stations</div>
                <div className="text-xl font-bold text-purple-600">{uploadResults?.station_count || '5'}</div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                <div className="text-sm text-gray-600">Correlation</div>
                <div className="text-xl font-bold text-orange-600">{uploadResults?.correlation?.toFixed(2) || '0.94'}</div>
              </div>
            </div>

            {/* Error Chart */}
            <div className="h-64 bg-white rounded-lg border p-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={uploadResults?.stations || mockValidationData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
                  <XAxis 
                    dataKey="station" 
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
                    label={{ value: 'Error (mm)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
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
                  <Bar dataKey="rmse" fill="#3b82f6" name="RMSE (mm)" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="mae" fill="#10b981" name="MAE (mm)" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Station Details */}
            <div className="space-y-2">
              <h4 className="font-medium">Station-wise Results</h4>
              <div className="space-y-2">
                {mockValidationData.map((station) => (
                  <div key={station.station} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                    <div className="flex items-center space-x-3">
                      {station.status === "good" && <CheckCircle className="h-4 w-4 text-chart-3" />}
                      {station.status === "warning" && <AlertCircle className="h-4 w-4 text-chart-2" />}
                      {station.status === "error" && <AlertCircle className="h-4 w-4 text-chart-4" />}
                      <span className="font-medium">{station.station}</span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm">
                      <span>RMSE: {station.rmse}mm</span>
                      <span>MAE: {station.mae}mm</span>
                      <Badge
                        variant={station.status === "good" ? "default" : "destructive"}
                        className={
                          station.status === "good"
                            ? "bg-chart-3"
                            : station.status === "warning"
                              ? "bg-chart-2"
                              : "bg-chart-4"
                        }
                      >
                        {station.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
