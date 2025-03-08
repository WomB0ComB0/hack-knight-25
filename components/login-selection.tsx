"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export function LoginSelection() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handlePatientLogin = () => {
    setIsLoading(true)
    // In a real app, this would show a login form first
    // For now, we'll just redirect to the dashboard
    setTimeout(() => {
      router.push("/dashboard")
    }, 500)
  }

  const handleRegister = () => {
    router.push("/register")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-[350px] shadow-lg">
        <CardContent className="flex flex-col items-center gap-4 p-6">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-8 w-8 text-blue-600"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-center">MedChain</h1>
          <p className="mb-4 text-center text-sm text-gray-500">Secure blockchain healthcare data management</p>

          <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={handlePatientLogin} disabled={isLoading}>
            <User className="mr-2 h-4 w-4" />
            Patient Login
          </Button>

          <div className="mt-4 text-center text-sm">
            <span className="text-gray-500">Don&apos;t have an account?</span>{" "}
            <button onClick={handleRegister} className="text-blue-600 hover:underline">
              Register
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

