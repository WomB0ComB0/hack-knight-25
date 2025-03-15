import { NextResponse } from 'next/server';
import type { Appointment } from '@/types/appointment';

// Dummy data
const appointments: Appointment[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john@example.com",
    date: "12/25/2023",
    visitTime: "10:00 AM",
    doctor: "Dr. Smith",
    condition: "Regular Checkup",
    smartContractKey: "0x123abc",
    avatar: "/placeholder.svg"
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane@example.com",
    date: "12/26/2023",
    visitTime: "2:30 PM",
    doctor: "Dr. Johnson",
    condition: "Follow-up",
    smartContractKey: "0x456def",
    avatar: "/placeholder.svg"
  }
];

export async function GET() {
  return NextResponse.json(appointments);
}

export async function POST(request: Request) {
  const appointment = await request.json() as Appointment;
  appointment.id = Date.now().toString();
  appointments.push(appointment);
  return NextResponse.json(appointment);
}