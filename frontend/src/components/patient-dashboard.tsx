"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/header";
import { NavigationSidebar } from "@/components/navigation-sidebar";
import { AppointmentTable } from "@/components/appointment-table";
import { DataAccessCard } from "@/components/data-access-card";
import { HealthSummaryCard } from "@/components/health-summary-card";
import type { Appointment } from "@/types/appointment";
import { useRouter } from "next/navigation";

export function PatientDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const router = useRouter();

  useEffect(() => {
    // Fetch appointments from API
    const fetchAppointments = async () => {
      const response = await fetch("/api/appointments");
      const data = await response.json();
      setAppointments(data);
    };
    fetchAppointments();
  }, []);

  const handleLogout = () => {
    router.push("/");
  };

  const handleAddAppointment = async (appointment: Appointment) => {
    const response = await fetch("/api/appointments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(appointment),
    });
    const newAppointment = await response.json();
    setAppointments([...appointments, newAppointment]);
  };

  const handleDeleteAppointment = async (id: string) => {
    await fetch(`/api/appointments/${id}`, {
      method: "DELETE",
    });
    setAppointments(
      appointments.filter((appointment) => appointment.id !== id)
    );
  };

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
  );
}
