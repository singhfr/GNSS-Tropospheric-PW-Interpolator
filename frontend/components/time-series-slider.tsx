"use client"

import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import { Play, Pause, SkipBack, SkipForward } from "lucide-react"
import { useState, useEffect } from "react"

interface TimeSeriesSliderProps {
  currentTime: Date
  onTimeChange: (time: Date) => void
}

export function TimeSeriesSlider({ currentTime, onTimeChange }: TimeSeriesSliderProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  // Demo time range matching the actual dataset (2024-01-01 full day)
  const startTime = new Date("2024-01-01T00:00:00Z")
  const endTime = new Date("2024-01-01T23:59:59Z") 
  const totalHours = 24

  // Calculate current hour based on the actual time, with bounds checking
  const currentHour = Math.max(0, Math.min(totalHours - 1, Math.floor((currentTime.getTime() - startTime.getTime()) / (1000 * 60 * 60))))

  const handleSliderChange = (value: number[]) => {
    const newTime = new Date(startTime.getTime() + value[0] * 60 * 60 * 1000)
    onTimeChange(newTime)
  }

  const handleSkipBack = () => {
    const newHour = Math.max(0, currentHour - 1)
    const newTime = new Date(startTime.getTime() + newHour * 60 * 60 * 1000)
    onTimeChange(newTime)
  }

  const handleSkipForward = () => {
    const newHour = Math.min(totalHours - 1, currentHour + 1)
    const newTime = new Date(startTime.getTime() + newHour * 60 * 60 * 1000)
    onTimeChange(newTime)
  }

  // Auto-play functionality
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying) {
      interval = setInterval(() => {
        const nextHour = (currentHour + 1) % totalHours
        const newTime = new Date(startTime.getTime() + nextHour * 60 * 60 * 1000)
        onTimeChange(newTime)
      }, 2000) // Change every 2 seconds
    }
    return () => clearInterval(interval)
  }, [isPlaying, currentHour, totalHours, startTime, onTimeChange])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Time Control</h3>
          <p className="text-sm text-muted-foreground">Current: {formatTime(currentTime)} UTC</p>
        </div>

        <div className="flex items-center space-x-2">
          <Button size="sm" variant="outline" onClick={handleSkipBack} disabled={currentHour === 0}>
            <SkipBack className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => setIsPlaying(!isPlaying)}>
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button size="sm" variant="outline" onClick={handleSkipForward} disabled={currentHour === totalHours - 1}>
            <SkipForward className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <Slider
          value={[currentHour]}
          onValueChange={handleSliderChange}
          max={totalHours - 1}
          min={0}
          step={1}
          className="w-full"
        />

        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{formatTime(startTime)}</span>
          <span>Jan 1, 2024</span>
          <span>{formatTime(endTime)}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="bg-secondary rounded p-2 text-center">
          <div className="font-medium">Data Points</div>
          <div className="text-lg font-bold text-primary">1,247</div>
        </div>
        <div className="bg-secondary rounded p-2 text-center">
          <div className="font-medium">Stations Active</div>
          <div className="text-lg font-bold text-chart-3">23</div>
        </div>
        <div className="bg-secondary rounded p-2 text-center">
          <div className="font-medium">Avg PW</div>
          <div className="text-lg font-bold text-chart-2">24.7mm</div>
        </div>
      </div>
    </div>
  )
}
