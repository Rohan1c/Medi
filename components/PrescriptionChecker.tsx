import React, { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Plus, Minus, Paperclip, FileText, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

interface PatientInfo {
  age: string;
  weight: string;
  allergies: string;
  conditions: string;
}

interface Prescription {
  medication: string;
  dosage: string;
  frequency: string;
  duration: string;
}

interface ValidationResult {
  overall: 'approved' | 'warning' | 'rejected';
  items: Array<{
    medication: string;
    status: 'approved' | 'warning' | 'rejected';
    message: string;
  }>;
  recommendations: string[];
}

export function PrescriptionChecker() {
  const [diagnosis, setDiagnosis] = useState('');
  const [patientInfo, setPatientInfo] = useState<PatientInfo>({
    age: '',
    weight: '',
    allergies: '',
    conditions: ''
  });
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([
    { medication: '', dosage: '', frequency: '', duration: '' }
  ]);
  const [attachedImage, setAttachedImage] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [prescriptionText, setPrescriptionText] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileAttach = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setAttachedImage(file);
    }
  };

  const addPrescription = () => {
    setPrescriptions([...prescriptions, { medication: '', dosage: '', frequency: '', duration: '' }]);
  };

  const removePrescription = (index: number) => {
    if (prescriptions.length > 1) {
      setPrescriptions(prescriptions.filter((_, i) => i !== index));
    }
  };

  const updatePrescription = (index: number, field: keyof Prescription, value: string) => {
    const updated = [...prescriptions];
    updated[index][field] = value;
    setPrescriptions(updated);
  };

  const parsePrescriptionText = (text: string): Prescription[] => {
    if (!text.trim()) return prescriptions;
    
    const lines = text.split(/[;\n]/).filter(line => line.trim());
    const parsed: Prescription[] = [];
    
    lines.forEach(line => {
      const parts = line.split(/\s+/);
      if (parts.length >= 2) {
        const medication = parts[0];
        const dosageMatch = line.match(/(\d+\s*(?:mg|g|ml|units?))/i);
        const frequencyMatch = line.match(/(once|twice|thrice|\d+\s*times?)\s*(?:daily|per\s*day|a\s*day)/i);
        const durationMatch = line.match(/(?:for\s*)?(\d+\s*(?:days?|weeks?|months?))/i);
        
        parsed.push({
          medication: medication,
          dosage: dosageMatch ? dosageMatch[1] : '',
          frequency: frequencyMatch ? frequencyMatch[0] : '',
          duration: durationMatch ? durationMatch[1] : ''
        });
      }
    });
    
    return parsed.length > 0 ? parsed : prescriptions;
  };

  const validatePrescription = (): ValidationResult => {
    const result: ValidationResult = {
      overall: 'approved',
      items: [],
      recommendations: [
        'Verify patient allergies before dispensing',
        'Monitor patient for adverse reactions',
        'Ensure proper patient education on medication usage',
        'Schedule appropriate follow-up appointments'
      ]
    };

    const age = parseInt(patientInfo.age);
    const allergies = patientInfo.allergies.toLowerCase();
    const diagnosisLower = diagnosis.toLowerCase();

    prescriptions.forEach((prescription, index) => {
      const med = prescription.medication.trim();
      const dose = prescription.dosage.trim();
      const freq = prescription.frequency.trim();
      const issues: string[] = [];
      let status: 'approved' | 'warning' | 'rejected' = 'approved';

      if (!med) {
        issues.push("Medication name is required");
        status = 'rejected';
      }

      if (!dose) {
        issues.push("Dosage is required");
        status = 'rejected';
      }

      // Allergy check
      if (med.toLowerCase().includes('penicillin') && allergies.includes('penicillin')) {
        issues.push("ALLERGY ALERT: Patient is allergic to penicillin");
        status = 'rejected';
      }

      // Age check
      if (!isNaN(age) && age < 16 && med.toLowerCase().includes('aspirin')) {
        issues.push("AGE WARNING: Aspirin not recommended for patients under 16");
        if (status === 'approved') status = 'warning';
      }

      // Frequency check
      if (med.toLowerCase().includes('ibuprofen') && freq.toLowerCase().includes('4 times')) {
        issues.push("DOSAGE WARNING: High frequency for ibuprofen, monitor for GI effects");
        if (status === 'approved') status = 'warning';
      }

      // Diagnosis matching
      if (diagnosisLower.includes('infection') && 
          !['antibiotic', 'amoxicillin', 'penicillin'].some(term => med.toLowerCase().includes(term))) {
        issues.push("INFO: Consider antibiotic for bacterial infection");
        if (status === 'approved') status = 'warning';
      }

      if (issues.length === 0) {
        issues.push("Prescription appears appropriate for the given diagnosis");
      }

      result.items.push({
        medication: med || `Medication ${index + 1}`,
        status,
        message: issues.join('. ')
      });
    });

    // Determine overall status
    if (result.items.some(item => item.status === 'rejected')) {
      result.overall = 'rejected';
    } else if (result.items.some(item => item.status === 'warning')) {
      result.overall = 'warning';
    }

    return result;
  };

  const handleValidate = () => {
    if (prescriptionText.trim()) {
      const parsed = parsePrescriptionText(prescriptionText);
      setPrescriptions(parsed);
    }
    const result = validatePrescription();
    setValidationResult(result);
  };

  const handleReset = () => {
    setDiagnosis('');
    setPatientInfo({ age: '', weight: '', allergies: '', conditions: '' });
    setPrescriptions([{ medication: '', dosage: '', frequency: '', duration: '' }]);
    setAttachedImage(null);
    setValidationResult(null);
    setPrescriptionText('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'rejected': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'status-approved border-l-4';
      case 'warning': return 'status-warning border-l-4';
      case 'rejected': return 'status-rejected border-l-4';
      default: return '';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto">
      {/* Left Column - Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Patient Information & Prescription
          </CardTitle>
          <CardDescription>
            Enter patient details and prescribed medications for validation
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Diagnosis */}
          <div className="space-y-2">
            <Label htmlFor="diagnosis">Medical Diagnosis *</Label>
            <Textarea
              id="diagnosis"
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="Enter the medical diagnosis..."
              rows={3}
            />
          </div>

          <Separator />

          {/* Patient Information */}
          <div className="space-y-4">
            <h3 className="font-medium">Patient Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age (years)</Label>
                <Input
                  id="age"
                  value={patientInfo.age}
                  onChange={(e) => setPatientInfo({...patientInfo, age: e.target.value})}
                  placeholder="Years"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  value={patientInfo.weight}
                  onChange={(e) => setPatientInfo({...patientInfo, weight: e.target.value})}
                  placeholder="kg"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="allergies">Known Allergies</Label>
              <Input
                id="allergies"
                value={patientInfo.allergies}
                onChange={(e) => setPatientInfo({...patientInfo, allergies: e.target.value})}
                placeholder="e.g., Penicillin, Sulfa drugs"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="conditions">Medical Conditions</Label>
              <Input
                id="conditions"
                value={patientInfo.conditions}
                onChange={(e) => setPatientInfo({...patientInfo, conditions: e.target.value})}
                placeholder="e.g., Diabetes, Hypertension"
              />
            </div>
          </div>

          <Separator />

          {/* Quick Text Input */}
          <div className="space-y-2">
            <Label htmlFor="prescription-text">Quick Prescription Entry</Label>
            <Textarea
              id="prescription-text"
              value={prescriptionText}
              onChange={(e) => setPrescriptionText(e.target.value)}
              placeholder="e.g., Paracetamol 500mg twice daily for 7 days; Ibuprofen 200mg once daily for 5 days"
              rows={3}
            />
          </div>

          {/* Prescribed Medications */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium">Prescribed Medications</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={addPrescription}
                className="h-8"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add
              </Button>
            </div>
            
            {prescriptions.map((prescription, index) => (
              <Card key={index} className="border-muted">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-sm">Medication {index + 1}</h4>
                    {prescriptions.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removePrescription(index)}
                        className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                      >
                        <Minus className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Medication Name</Label>
                      <Input
                        value={prescription.medication}
                        onChange={(e) => updatePrescription(index, 'medication', e.target.value)}
                        placeholder="e.g., Amoxicillin"
                        className="h-8"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Dosage</Label>
                      <Input
                        value={prescription.dosage}
                        onChange={(e) => updatePrescription(index, 'dosage', e.target.value)}
                        placeholder="e.g., 500mg"
                        className="h-8"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Frequency</Label>
                      <Input
                        value={prescription.frequency}
                        onChange={(e) => updatePrescription(index, 'frequency', e.target.value)}
                        placeholder="e.g., 2 times daily"
                        className="h-8"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Duration</Label>
                      <Input
                        value={prescription.duration}
                        onChange={(e) => updatePrescription(index, 'duration', e.target.value)}
                        placeholder="e.g., 7 days"
                        className="h-8"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleFileAttach}
              className="flex-1 file-upload-zone"
            >
              <Paperclip className="h-4 w-4 mr-2" />
              Attach Image
            </Button>
            <Button
              onClick={handleValidate}
              className="flex-1"
            >
              Validate Prescription
            </Button>
            <Button
              variant="outline"
              onClick={handleReset}
            >
              Reset
            </Button>
          </div>

          {attachedImage && (
            <div className="flex items-center gap-3 p-3 bg-muted rounded-md">
              <ImageWithFallback
                src={URL.createObjectURL(attachedImage)}
                alt="Prescription attachment"
                className="w-12 h-12 object-cover rounded"
              />
              <div className="flex-1">
                <p className="text-sm font-medium">{attachedImage.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(attachedImage.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAttachedImage(null)}
                className="h-8 w-8 p-0"
              >
                ×
              </Button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.pdf"
            onChange={handleFileChange}
            className="hidden"
          />
        </CardContent>
      </Card>

      {/* Right Column - Validation Results */}
      <Card>
        <CardHeader>
          <CardTitle>Validation Results</CardTitle>
          <CardDescription>
            Review prescription safety and appropriateness
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {!validationResult ? (
            <div className="text-center py-8">
              <div className="text-muted-foreground mb-2">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Enter prescription details and click 'Validate Prescription' to see results</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Overall Status */}
              <Alert className={getStatusColor(validationResult.overall)}>
                <div className="flex items-center gap-2">
                  {getStatusIcon(validationResult.overall)}
                  <AlertDescription className="font-medium">
                    {validationResult.overall === 'approved' && "✅ Prescription Approved - All medications appear safe and appropriate"}
                    {validationResult.overall === 'warning' && "⚠️ Prescription Approved with Warnings - Some concerns identified, review recommended"}
                    {validationResult.overall === 'rejected' && "❌ Prescription Requires Review - Critical issues found, do not dispense"}
                  </AlertDescription>
                </div>
              </Alert>

              <Separator />

              {/* Individual Medication Results */}
              <div className="space-y-3">
                <h4 className="font-medium">Medication Analysis</h4>
                {validationResult.items.map((item, index) => (
                  <div
                    key={index}
                    className={`border-l-4 rounded-md p-3 ${getStatusColor(item.status)}`}
                  >
                    <div className="flex items-start gap-2">
                      {getStatusIcon(item.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm">{item.medication}</span>
                          <Badge 
                            variant={item.status === 'approved' ? 'default' : 
                                   item.status === 'warning' ? 'secondary' : 'destructive'}
                            className="text-xs"
                          >
                            {item.status.toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.message}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <Separator />

              {/* Recommendations */}
              <div className="space-y-2">
                <h4 className="font-medium">General Recommendations</h4>
                <ul className="space-y-1">
                  {validationResult.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Attached Image */}
              {attachedImage && (
                <>
                  <Separator />
                  <div className="space-y-2">
                    <h4 className="font-medium">Attached Prescription</h4>
                    <ImageWithFallback
                      src={URL.createObjectURL(attachedImage)}
                      alt="Prescription attachment"
                      className="max-w-full rounded-md border"
                    />
                  </div>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}