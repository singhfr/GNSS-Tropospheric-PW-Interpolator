"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { BarChart3, Upload, Shield, Info, Satellite } from "lucide-react"

interface SidebarProps {
  activeView: string
  onViewChange: (view: string) => void
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "upload", label: "Upload Data", icon: Upload },
    { id: "validation", label: "Error Validation", icon: Shield },
    { id: "about", label: "About", icon: Info },
  ]

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <Satellite className="h-8 w-8 text-blue-400" />
          <div>
            <h2 className="font-bold text-white">GNSS PW</h2>
            <p className="text-xs text-gray-400">Interpolator</p>
          </div>
        </div>
      </div>

      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <Button
              key={item.id}
              variant={activeView === item.id ? "default" : "ghost"}
              className={cn(
                "w-full justify-start transition-colors",
                activeView === item.id
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white",
              )}
              onClick={() => onViewChange(item.id)}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          )
        })}
      </nav>
    </div>
  )
}
