import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { GraduationCap, Calendar, MapPin, ExternalLink } from 'lucide-react';
import { education } from '../data/content';

const Education = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl lg:text-5xl font-bold">Education & Training</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          My academic background in mechanical and aerospace engineering
        </p>
      </div>

      {/* Education Timeline */}
      <div className="space-y-8">
        {education.map((edu, index) => (
          <Card key={edu.id} className="relative">
            {/* Timeline connector */}
            {index < education.length - 1 && (
              <div className="absolute left-8 top-20 w-0.5 h-16 bg-border hidden md:block"></div>
            )}
            
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row md:items-start gap-6">
                {/* Timeline dot */}
                <div className="hidden md:flex w-4 h-4 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                
                <div className="flex-1 space-y-4">
                  {/* Header */}
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <h2 className="text-2xl font-bold flex items-center">
                          <GraduationCap className="h-6 w-6 mr-2 text-primary" />
                          {edu.degree}
                        </h2>
                        <h3 className="text-lg font-semibold text-primary">{edu.institution}</h3>
                      </div>
                      <Badge variant="outline">
                        {edu.startDate} - {edu.endDate}
                      </Badge>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row sm:items-center gap-4 text-muted-foreground">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {edu.location}
                      </div>
                      {edu.grade && (
                        <div className="flex items-center">
                          <span className="font-medium">Grade: {edu.grade}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Thesis */}
                  {edu.thesis && (
                    <div className="bg-muted/50 p-4 rounded-lg">
                      <h4 className="font-semibold mb-2">Master's Thesis:</h4>
                      <p className="text-muted-foreground italic">{edu.thesis}</p>
                    </div>
                  )}

                  {/* Website Link */}
                  {edu.website && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={edu.website} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Visit Institution
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Academic Focus Areas */}
      <div className="mt-16 space-y-8">
        <h2 className="text-3xl font-bold text-center">Academic Focus Areas</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
                  <GraduationCap className="h-4 w-4 text-primary" />
                </div>
                Master's Research
              </h3>
              <div className="space-y-3">
                <p className="text-muted-foreground">
                  Specialized in mobile robotics and intelligent control systems, focusing on:
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Path planning algorithms for mobile robots
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Fuzzy logic control systems
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Dynamic obstacle avoidance
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Social robotics and human-robot interaction
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
                  <GraduationCap className="h-4 w-4 text-primary" />
                </div>
                Undergraduate Foundation
              </h3>
              <div className="space-y-3">
                <p className="text-muted-foreground">
                  Built a strong foundation in aerospace engineering, covering:
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Aerodynamics and flight mechanics
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Control systems and automation
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Mathematical modeling and simulation
                  </li>
                  <li className="flex items-start">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    Engineering design and analysis
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Certifications & Additional Training */}
      <div className="mt-16 p-8 bg-muted/30 rounded-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Continuous Learning</h2>
        <div className="text-center space-y-4">
          <p className="text-muted-foreground">
            I believe in continuous learning and staying updated with the latest developments in robotics, 
            AI, and embedded systems. My academic foundation provides the theoretical knowledge, while 
            hands-on projects and research keep me at the forefront of technological advancement.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Badge variant="secondary">Research Publications</Badge>
            <Badge variant="secondary">Conference Presentations</Badge>
            <Badge variant="secondary">Technical Workshops</Badge>
            <Badge variant="secondary">Industry Collaboration</Badge>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Education;

