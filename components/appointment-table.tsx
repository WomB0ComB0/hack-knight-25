"use client"

import type React from "react"

import { useState } from "react"
import { Check, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { Appointment } from "@/types/appointment"

interface AppointmentTableProps {
  appointments: Appointment[]
  onAddAppointment: (appointment: Appointment) => void
  onDeleteAppointment: (id: string) => void
}

export function AppointmentTable({ appointments, onAddAppointment, onDeleteAppointment }: AppointmentTableProps) {
  const [newAppointment, setNewAppointment] = useState<Partial<Appointment>>({
    name: "",
    email: "",
    date: "",
    visitTime: "",
    doctor: "",
    condition: "",
    smartContractKey: "",
    avatar: "/placeholder.svg?height=32&width=32",
  })
  const [open, setOpen] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setNewAppointment({ ...newAppointment, [name]: value })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const appointment: Appointment = {
      id: Date.now().toString(),
      name: newAppointment.name || "",
      email: newAppointment.email || "",
      date: newAppointment.date || "",
      visitTime: newAppointment.visitTime || "",
      doctor: newAppointment.doctor || "",
      condition: newAppointment.condition || "",
      smartContractKey: newAppointment.smartContractKey || `0x${Math.random().toString(16).slice(2, 10)}`,
      avatar: "/placeholder.svg?height=32&width=32",
    }

    onAddAppointment(appointment)
    setNewAppointment({
      name: "",
      email: "",
      date: "",
      visitTime: "",
      doctor: "",
      condition: "",
      smartContractKey: "",
      avatar: "/placeholder.svg?height=32&width=32",
    })
    setOpen(false)
  }

  return (
    <div className="rounded-lg border bg-white shadow">
      <div className="flex items-center justify-between p-4">
        <h2 className="text-lg font-semibold">Appointment Activity</h2>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
              <Plus className="mr-2 h-4 w-4" />
              Add Appointment
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Appointment</DialogTitle>
              <DialogDescription>Enter the details for your new appointment.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="name"
                    name="name"
                    value={newAppointment.name}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="email" className="text-right">
                    Email
                  </Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={newAppointment.email}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="date" className="text-right">
                    Date
                  </Label>
                  <Input
                    id="date"
                    name="date"
                    type="text"
                    placeholder="MM/DD/YYYY"
                    value={newAppointment.date}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="visitTime" className="text-right">
                    Visit Time
                  </Label>
                  <Input
                    id="visitTime"
                    name="visitTime"
                    value={newAppointment.visitTime}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="doctor" className="text-right">
                    Doctor
                  </Label>
                  <Input
                    id="doctor"
                    name="doctor"
                    value={newAppointment.doctor}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="condition" className="text-right">
                    Condition
                  </Label>
                  <Input
                    id="condition"
                    name="condition"
                    value={newAppointment.condition}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="smartContractKey" className="text-right">
                    Smart Contract Key
                  </Label>
                  <Input
                    id="smartContractKey"
                    name="smartContractKey"
                    value={newAppointment.smartContractKey}
                    onChange={handleInputChange}
                    placeholder="0x..."
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                  Add Appointment
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Visit Time</TableHead>
              <TableHead>Doctor</TableHead>
              <TableHead>Condition</TableHead>
              <TableHead>Smart Contract Key</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {appointments.map((appointment) => (
              <TableRow key={appointment.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    <img
                      src={appointment.avatar || "/placeholder.svg"}
                      alt={appointment.name}
                      className="h-8 w-8 rounded-full"
                    />
                    <span>{appointment.name}</span>
                  </div>
                </TableCell>
                <TableCell>{appointment.email}</TableCell>
                <TableCell>{appointment.date}</TableCell>
                <TableCell>{appointment.visitTime}</TableCell>
                <TableCell>{appointment.doctor}</TableCell>
                <TableCell>{appointment.condition}</TableCell>
                <TableCell className="font-mono text-xs">
                  {appointment.smartContractKey || `0x${Math.random().toString(16).slice(2, 10)}`}
                </TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Check className="h-4 w-4 text-green-500" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => onDeleteAppointment(appointment.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

