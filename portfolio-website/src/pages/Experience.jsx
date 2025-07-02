import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MapPin, Calendar } from 'lucide-react';
import { workExperience } from '../data/content';

const Experience = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl lg:text-5xl font-bold">Work Experience</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          My professional journey in robotics, embedded systems, and AI-driven control
        </p>
      </div>

      {/* Experience Timeline */}
      <div className="space-y-8">
        {workExperience.map((experience, index) => (
          <Card key={experience.id} className="relative">
            {/* Timeline connector */}
            {index < workExperience.length - 1 && (
              <div className="absolute left-8 top-20 w-0.5 h-16 bg-border hidden md:block"></div>
            )}
            
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row md:items-start gap-6">
                {/* Timeline dot */}
                <div className="hidden md:flex w-4 h-4 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                
                <div className="flex-1 space-y-4">
                  {/* Header */}
                  <div className="space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <h2 className="text-2xl font-bold">{experience.position}</h2>
                      <Badge variant="outline" className="w-fit">
                        {experience.startDate} - {experience.endDate}
                      </Badge>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row sm:items-center gap-4 text-muted-foreground">
                      <div className="flex items-center">
                        <span className="font-semibold text-foreground">{experience.company}</span>
                      </div>
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {experience.location}
                      </div>
                    </div>
                  </div>

                  {/* Responsibilities */}
                  <div className="space-y-3">
                    {experience.description.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-muted-foreground leading-relaxed">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Skills Summary */}
      <div className="mt-16 p-8 bg-muted/30 rounded-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Key Technologies & Skills</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Embedded Systems</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="secondary">STM32</Badge>
              <Badge variant="secondary">FreeRTOS</Badge>
              <Badge variant="secondary">ARM</Badge>
              <Badge variant="secondary">ESP32</Badge>
            </div>
          </div>
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Robotics & AI</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="secondary">ROS/ROS2</Badge>
              <Badge variant="secondary">Gazebo</Badge>
              <Badge variant="secondary">Machine Learning</Badge>
              <Badge variant="secondary">Computer Vision</Badge>
            </div>
          </div>
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Programming</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="secondary">C/C++</Badge>
              <Badge variant="secondary">Python</Badge>
              <Badge variant="secondary">MATLAB</Badge>
              <Badge variant="secondary">Git</Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Experience;

