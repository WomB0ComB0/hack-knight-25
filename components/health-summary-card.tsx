import { Activity, Heart, TreesIcon as Lungs, Weight } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function HealthSummaryCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          Health Summary
        </CardTitle>
        <CardDescription>Your recent health metrics</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-red-500" />
                <span className="text-sm font-medium">Blood Pressure</span>
              </div>
              <p className="mt-2 text-2xl font-semibold">120/80</p>
              <p className="text-xs text-gray-500">Last updated: 2 days ago</p>
            </div>
            <div className="rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <Lungs className="h-5 w-5 text-blue-500" />
                <span className="text-sm font-medium">Oxygen Level</span>
              </div>
              <p className="mt-2 text-2xl font-semibold">98%</p>
              <p className="text-xs text-gray-500">Last updated: 2 days ago</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-500" />
                <span className="text-sm font-medium">Heart Rate</span>
              </div>
              <p className="mt-2 text-2xl font-semibold">72 bpm</p>
              <p className="text-xs text-gray-500">Last updated: 2 days ago</p>
            </div>
            <div className="rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <Weight className="h-5 w-5 text-purple-500" />
                <span className="text-sm font-medium">Weight</span>
              </div>
              <p className="mt-2 text-2xl font-semibold">165 lbs</p>
              <p className="text-xs text-gray-500">Last updated: 1 week ago</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

