"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { NavigationSidebar } from "@/components/navigation-sidebar"
import { AppointmentTable } from "@/components/appointment-table"
import { DataAccessCard } from "@/components/data-access-card"
import { HealthSummaryCard } from "@/components/health-summary-card"
import type { Appointment } from "@/types/appointment"
import { useRouter } from "next/navigation"

export function PatientDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([
    {
      id: "1",
      name: "Leslie Alexander",
      email: "leslie.alexander@example.com",
      date: "10/10/2020",
      visitTime: "09:15-09:45am",
      doctor: "Dr. Jacob Jones",
      condition: "Migraine Stage II",
      smartContractKey: "0x7a3d4f8c2e1b",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    {
      id: "2",
      name: "Ronald Richards",
      email: "ronald.richards@example.com",
      date: "10/12/2020",
      visitTime: "12:00-12:45pm",
      doctor: "Dr. Theresa Webb",
      condition: "Depression",
      smartContractKey: "0x2c4e6a8f1d3b",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    {
      id: "3",
      name: "Jane Cooper",
      email: "jane.cooper@example.com",
      date: "10/13/2020",
      visitTime: "01:15-01:45pm",
      doctor: "Dr. Jacob Jones",
      condition: "Arthritis",
      smartContractKey: "0xf1e3d5c7b9a2",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    {
      id: "4",
      name: "Robert Fox",
      email: "robert.fox@gmail.com",
      date: "10/14/2020",
      visitTime: "02:00-02:45pm",
      doctor: "Dr. Arlene McCoy",
      condition: "Fracture",
      smartContractKey: "0x3b5a7d9c1e8f",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    {
      id: "5",
      name: "Jenny Wilson",
      email: "jenny.wilson@example.com",
      date: "10/15/2020",
      visitTime: "12:00-12:45pm",
      doctor: "Dr. Esther Howard",
      condition: "Depression",
      smartContractKey: "0x8c2a4e6d1f3b",
      avatar: "/placeholder.svg?height=32&width=32",
    },
  ])

  const router = useRouter()

  const handleLogout = () => {
    router.push("/")
  }

  const handleAddAppointment = (appointment: Appointment) => {
    setAppointments([...appointments, appointment])
  }

  const handleDeleteAppointment = (id: string) => {
    setAppointments(appointments.filter((appointment) => appointment.id !== id))
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <NavigationSidebar onLogout={handleLogout} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mb-8">
            <AppointmentTable
              appointments={appointments}
              onAddAppointment={handleAddAppointment}
              onDeleteAppointment={handleDeleteAppointment}
            />
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <DataAccessCard />
            <HealthSummaryCard />
          </div>
        </main>
      </div>
    </div>
  )
}
