import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Cpu, Code, Cog, Zap } from 'lucide-react';
import { skills } from '../data/content';

const Skills = () => {
  const skillCategories = [
    {
      title: "Embedded Software Development",
      icon: Cpu,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      skills: skills["Embedded Software Development"]
    },
    {
      title: "Real Time Operating Systems",
      icon: Cog,
      color: "text-green-500",
      bgColor: "bg-green-500/10",
      skills: skills["Real Time Operating Systems"]
    },
    {
      title: "Software Development and Version Control",
      icon: Code,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
      skills: skills["Software Development and Version Control"]
    }
  ];

  const additionalSkills = [
    { name: "Machine Learning", level: 85 },
    { name: "Computer Vision", level: 80 },
    { name: "Control Systems", level: 90 },
    { name: "Signal Processing", level: 75 },
    { name: "3D Modeling", level: 70 },
    { name: "PCB Design", level: 65 }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl lg:text-5xl font-bold">Skills & Expertise</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Technical skills and expertise developed through years of hands-on experience in robotics and embedded systems
        </p>
      </div>

      {/* Main Skill Categories */}
      <div className="grid lg:grid-cols-3 gap-8 mb-16">
        {skillCategories.map((category, index) => {
          const IconComponent = category.icon;
          return (
            <Card key={index} className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-lg ${category.bgColor} flex items-center justify-center`}>
                    <IconComponent className={`h-5 w-5 ${category.color}`} />
                  </div>
                  <span className="text-lg">{category.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {category.skills.map((skill, skillIndex) => (
                    <Badge key={skillIndex} variant="secondary" className="text-sm">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Additional Skills with Progress Bars */}
      <div className="space-y-8">
        <h2 className="text-3xl font-bold text-center">Additional Technical Skills</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          {additionalSkills.map((skill, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{skill.name}</span>
                    <span className="text-sm text-muted-foreground">{skill.level}%</span>
                  </div>
                  <Progress value={skill.level} className="h-2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Expertise Areas */}
      <div className="mt-16 space-y-8">
        <h2 className="text-3xl font-bold text-center">Areas of Expertise</h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="text-center p-6">
            <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Zap className="h-6 w-6 text-red-500" />
            </div>
            <h3 className="font-semibold mb-2">Real-Time Systems</h3>
            <p className="text-sm text-muted-foreground">
              Design and implementation of real-time embedded systems with strict timing constraints
            </p>
          </Card>

          <Card className="text-center p-6">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Cpu className="h-6 w-6 text-blue-500" />
            </div>
            <h3 className="font-semibold mb-2">Autonomous Navigation</h3>
            <p className="text-sm text-muted-foreground">
              Path planning, obstacle avoidance, and intelligent navigation for mobile robots
            </p>
          </Card>

          <Card className="text-center p-6">
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Cog className="h-6 w-6 text-green-500" />
            </div>
            <h3 className="font-semibold mb-2">Control Systems</h3>
            <p className="text-sm text-muted-foreground">
              Advanced control algorithms including fuzzy logic, MPC, and reinforcement learning
            </p>
          </Card>

          <Card className="text-center p-6">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Code className="h-6 w-6 text-purple-500" />
            </div>
            <h3 className="font-semibold mb-2">AI Integration</h3>
            <p className="text-sm text-muted-foreground">
              Integration of machine learning and AI algorithms into embedded and robotic systems
            </p>
          </Card>
        </div>
      </div>

      {/* Tools & Technologies */}
      <div className="mt-16 p-8 bg-muted/30 rounded-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Development Tools & Platforms</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Development Environments</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="outline">Keil µVision</Badge>
              <Badge variant="outline">STM32CubeIDE</Badge>
              <Badge variant="outline">Arduino IDE</Badge>
              <Badge variant="outline">VS Code</Badge>
              <Badge variant="outline">MATLAB/Simulink</Badge>
            </div>
          </div>
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Simulation & Modeling</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="outline">Gazebo</Badge>
              <Badge variant="outline">RViz</Badge>
              <Badge variant="outline">MATLAB/Simulink</Badge>
              <Badge variant="outline">SolidWorks</Badge>
              <Badge variant="outline">Altium Designer</Badge>
            </div>
          </div>
          <div className="text-center space-y-3">
            <h3 className="font-semibold">Version Control & CI/CD</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="outline">Git</Badge>
              <Badge variant="outline">GitHub</Badge>
              <Badge variant="outline">GitLab</Badge>
              <Badge variant="outline">CMake</Badge>
              <Badge variant="outline">Catkin</Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Skills;

