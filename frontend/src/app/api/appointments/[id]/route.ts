import { NextResponse } from 'next/server';

// Reference to the dummy data from the parent route
declare const appointments: any[];

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id;
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
