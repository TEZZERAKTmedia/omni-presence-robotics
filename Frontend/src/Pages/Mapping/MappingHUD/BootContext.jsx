const BootContext = createContext()
function BootProvider({ children }) {
  const [currentStep, setCurrentStep] = useState(null)
  const [bootComplete, setBootComplete] = useState(false)

  const startBoot = async () => {
    for (const step of bootSteps) {
      setCurrentStep(step.label)
      const res = await fetch(`/boot/step/${step.id}`, { method: "POST" })
      if (res.ok) continue
      else return setCurrentStep("⚠️ Failed on " + step.label)
    }
    setBootComplete(true)
  }

  return (
    <BootContext.Provider value={{ currentStep, startBoot, bootComplete }}>
      {children}
    </BootContext.Provider>
  )
}
