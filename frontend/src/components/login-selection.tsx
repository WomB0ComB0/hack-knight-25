"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { User, LogIn, UserPlus, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { auth } from "@/utils/api"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { toast } from "@/components/ui/use-toast"

// Define the response types
interface RegisterResponse {
  message: string;
  user_id: string;
  blockchain_id: string;
  role: string;
  api_key: string;
}

export function LoginSelection() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [loginDialogOpen, setLoginDialogOpen] = useState(false)
  const [registerDialogOpen, setRegisterDialogOpen] = useState(false)

  const [loginEmail, setLoginEmail] = useState("")
  const [loginApiKey, setLoginApiKey] = useState("")

  const [registerName, setRegisterName] = useState("")
  const [registerEmail, setRegisterEmail] = useState("")
  const [registerRole, setRegisterRole] = useState<'patient' | 'healthcare_provider'>('patient')
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setIsLoading(true)

      // Validate API key
      const userData = await auth.validate(loginApiKey)

      // Store user data and API key
      auth.storeUserData(loginApiKey, userData)

      toast({
        title: "Login successful",
        description: "Welcome back to MedChain!"
      })

      // Redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      console.error("Login failed:", error)
      toast({
        title: "Login failed",
        description: "Invalid API key. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setIsLoading(true)
      setError(null);

      // Register new user
      const response = await auth.register(registerName, registerEmail, registerRole) as RegisterResponse

      // Store user data and API key
      auth.storeUserData(response.api_key, {
        id: response.user_id,
        blockchain_id: response.blockchain_id,
        name: registerName,
        email: registerEmail,
        role: registerRole
      })

      toast({
        title: "Registration successful",
        description: "Welcome to MedChain! Your blockchain wallet has been created."
      })

      // Redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
      console.error("Registration failed:", error)
      toast({
        title: "Registration failed",
        description: "Could not create your account. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
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
          <h1 className="text-center text-2xl font-bold">MedChain</h1>
          <p className="mb-4 text-center text-sm text-gray-500">Secure blockchain healthcare data management</p>

          <Dialog open={loginDialogOpen} onOpenChange={setLoginDialogOpen}>
            <DialogTrigger asChild>
              <Button className="w-full bg-blue-600 hover:bg-blue-700">
                <LogIn className="mr-2 h-4 w-4" />
                Login
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleLogin}>
                <DialogHeader>
                  <DialogTitle>Login to MedChain</DialogTitle>
                  <DialogDescription>
                    Enter your credentials to access your healthcare data.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="your.email@example.com"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="apiKey">API Key</Label>
                    <Input
                      id="apiKey"
                      value={loginApiKey}
                      onChange={(e) => setLoginApiKey(e.target.value)}
                      placeholder="Enter your API key"
                      required
                    />
                    <p className="text-xs text-gray-500">
                      Your API key is used to authenticate your access to the blockchain.
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={isLoading}>
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Login
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={registerDialogOpen} onOpenChange={setRegisterDialogOpen}>
            <DialogTrigger asChild>
              <Button className="w-full bg-green-600 hover:bg-green-700">
                <UserPlus className="mr-2 h-4 w-4" />
                Register
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleRegister}>
                <DialogHeader>
                  <DialogTitle>Register for MedChain</DialogTitle>
                  <DialogDescription>
                    Create an account to start managing your healthcare data.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={registerName}
                      onChange={(e) => setRegisterName(e.target.value)}
                      placeholder="Your name"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={registerEmail}
                      onChange={(e) => setRegisterEmail(e.target.value)}
                      placeholder="your.email@example.com"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="role">Role</Label>
                    <select
                      id="role"
                      value={registerRole}
                      onChange={(e) => setRegisterRole(e.target.value as 'patient' | 'healthcare_provider')}
                      required
                      className="border border-gray-300 rounded-md p-2"
                    >
                      <option value="patient">Patient</option>
                      <option value="healthcare_provider">Healthcare Provider</option>
                    </select>
                  </div>
                </div>
                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-4">
                    <p>{error}</p>
                  </div>
                )}
                <DialogFooter>
                  <Button type="submit" disabled={isLoading}>
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Register
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          <div className="mt-4 text-center text-sm">
            <span className="text-gray-500">Don&apos;t have an account?</span>{" "}
            <button onClick={() => setRegisterDialogOpen(true)} className="text-blue-600 hover:underline">
              Register
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
