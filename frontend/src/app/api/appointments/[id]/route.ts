import type { NextRequest } from 'next/server';
import type { Appointment } from '@/types/appointment';
import { NextResponse } from 'next/server';

declare const appointments: Appointment[];

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const index = appointments.findIndex(apt => apt.id === id);
  
  if (index === -1) {
    return NextResponse.json(
      { error: "Appointment not found" },
      { status: 404 }
    );
  }

  appointments.splice(index, 1);
  return NextResponse.json({ success: true });
}