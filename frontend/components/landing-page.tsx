import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Satellite, MapPin, TrendingUp, Shield } from "lucide-react"
import Link from "next/link"

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-bold text-balance">GNSS Tropospheric PW Interpolator</h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto text-pretty">
              Advanced atmospheric science dashboard for real-time GNSS tropospheric precipitable water interpolation
              and analysis
            </p>
          </div>

          <div className="flex justify-center">
            <Link href="/dashboard">
              <Button size="lg" className="text-lg px-8 py-6">
                Start Dashboard
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
          <Card className="text-center">
            <CardHeader>
              <Satellite className="h-12 w-12 mx-auto text-primary" />
              <CardTitle>GNSS Integration</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Real-time integration with GNSS station networks for accurate tropospheric measurements
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <MapPin className="h-12 w-12 mx-auto text-primary" />
              <CardTitle>Interactive Mapping</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Advanced heatmap visualization with interpolated precipitable water values across regions
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <TrendingUp className="h-12 w-12 mx-auto text-primary" />
              <CardTitle>Time-Series Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Comprehensive temporal analysis with interactive sliders for historical data exploration
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <Shield className="h-12 w-12 mx-auto text-primary" />
              <CardTitle>Error Validation</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Advanced validation tools with RMSE/MAE calculations for data quality assurance
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Technical Details */}
        <div className="mt-16 text-center">
          <Card className="max-w-4xl mx-auto">
            <CardHeader>
              <CardTitle className="text-2xl">Research-Grade Atmospheric Analysis</CardTitle>
              <CardDescription className="text-lg">
                Built for atmospheric scientists and meteorological researchers
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                This dashboard provides comprehensive tools for analyzing tropospheric precipitable water using GNSS
                data. Features include real-time interpolation algorithms, forecast modeling, and validation against
                independent datasets.
              </p>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <span className="bg-secondary px-3 py-1 rounded-full">Zenith Wet Delay Processing</span>
                <span className="bg-secondary px-3 py-1 rounded-full">Spatial Interpolation</span>
                <span className="bg-secondary px-3 py-1 rounded-full">Forecast Extrapolation</span>
                <span className="bg-secondary px-3 py-1 rounded-full">Quality Control</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
