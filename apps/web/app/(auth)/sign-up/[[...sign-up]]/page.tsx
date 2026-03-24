import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-950 to-brand-800">
      <div className="w-full max-w-md space-y-8 px-4">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">Uportai</h1>
          <p className="mt-2 text-brand-200 text-sm">Start your free trial — no credit card required</p>
        </div>
        <SignUp
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "rounded-xl shadow-2xl",
            },
          }}
        />
      </div>
    </div>
  );
}
