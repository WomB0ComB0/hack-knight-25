"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/header";
import { NavigationSidebar } from "@/components/navigation-sidebar";
import { AppointmentTable } from "@/components/appointment-table";
import { DataAccessCard } from "@/components/data-access-card";
import { HealthSummaryCard } from "@/components/health-summary-card";
import { BlockchainInfoCard } from "@/components/blockchain-info-card"; 
import type { Appointment } from "@/types/appointment";
import { useRouter } from "next/navigation";
import { auth } from "@/utils/api";

export function PatientDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [userData, setUserData] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const storedUserData = auth.getUserData();
    if (storedUserData) {
      setUserData(storedUserData);
    } else {
      // Redirect to login if not authenticated
      router.push("/");
    }

    // Fetch appointments from API
    const fetchAppointments = async () => {
      try {
        const response = await fetch("/api/appointments");
        const data = await response.json();
        // Add type assertion to confirm data is of type Appointment[]
        setAppointments(data as Appointment[]);
      } catch (error) {
        console.error("Error fetching appointments:", error);
        // Use sample data if API fails
        setAppointments([
          {
            id: "1",
            name: "Annual Checkup",
            email: "patient@example.com",
            date: "06/15/2024",
            visitTime: "10:30 AM",
            doctor: "Dr. Smith",
            condition: "Routine",
            smartContractKey: "0x72f5a93d",
            avatar: "/placeholder.svg?height=32&width=32",
          },
        ]);
      }
    };
    fetchAppointments();
  }, [router]);

  const handleLogout = () => {
    auth.clearUserData();
    router.push("/");
  };

  const handleAddAppointment = async (appointment: Appointment) => {
    try {
      const response = await fetch("/api/appointments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(appointment),
      });
      const newAppointment = await response.json();
      setAppointments([...appointments, newAppointment as Appointment]);
    } catch (error) {
      console.error("Error adding appointment:", error);
      // Add locally if API fails
      setAppointments([...appointments, appointment]);
    }
  };

  const handleDeleteAppointment = async (id: string) => {
    try {
      await fetch(`/api/appointments/${id}`, {
        method: "DELETE",
      });
    } catch (error) {
      console.error("Error deleting appointment:", error);
    }
    setAppointments(
      appointments.filter((appointment) => appointment.id !== id)
    );
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <NavigationSidebar onLogout={handleLogout} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header userInfo={userData} />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mb-8">
            <AppointmentTable
              appointments={appointments}
              onAddAppointment={handleAddAppointment}
              onDeleteAppointment={handleDeleteAppointment}
            />
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <DataAccessCard />
            <HealthSummaryCard />
            <BlockchainInfoCard />
          </div>
        </main>
      </div>
    </div>
  );
}
