/*
 * CustomAgent.java
 *
 * Copyright 2007 Sun Microsystems, Inc.  All Rights Reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Sun Microsystems nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Created on Jul 25, 2007, 11:42:49 AM
 *
 */

/*
 * The original example was written by Daniel Fuchs.
 * 
 * JccJmxAgent was heavily customzied and partly rewritten by Christian Heimes
 * to support stopping and starting of agents and to work around quirks.
 */

package de.semantics.jccjmx;

import javax.management.MBeanServer;
import javax.management.remote.JMXConnectorServer;
import javax.management.remote.JMXConnectorServerFactory;
import javax.management.remote.JMXServiceURL;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.rmi.activation.ActivationException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.RemoteException;
import java.rmi.AccessException;
import java.util.HashMap;

/**
 * This CustomAgent will start an RMI Connector Server using only
 * port "example.rmi.agent.port".
 * 
 * @author dfuchs
 * @author Christian Heimes <c.heimes@semantics.de>
 */
public class JccJmxAgent {

    public static String DEFAULT_HOST = "127.0.0.1";
    public static int DEFAULT_PORT = 11111;
    
    private String host;
    private int port;
    private JMXConnectorServer cs;
    private CleanThread cleanthread;
    private Registry registry;

    public JccJmxAgent(String host, int port) throws IOException {
        this.host = host;
        this.port = port;
        this.cs = null;
        this.registry = null;
        
        // start clean thread
        cleanthread = new CleanThread();
        cleanthread.start();
        
    }
    
    public JccJmxAgent(int port) throws IOException {
        this(DEFAULT_HOST, port);
    }

    public JccJmxAgent() throws IOException {
        this(DEFAULT_HOST, DEFAULT_PORT);
    }
    
    public String getHostname() {
        return host;
    }
    
    public int getPort() {
        return port;
    }
    
    public String getServiceURL() {
        return "service:jmx:rmi://" + host + ":" + port + "/jndi/rmi://" + host + ":" + port + "/jmxrmi";
    }
    
    public void start() throws IOException {
        if (cleanthread == null) {
            cleanthread = new CleanThread();
            cleanthread.start();
        }

        if (cs == null) {
            createConnectorServer();
            cs.start();
            cleanthread.setCS(cs);
        }
    }
    
    public void stop() throws IOException {
        if (cs != null && cs.isActive()) {
            cs.stop();
            cs = null;
        }
    }
    
    public boolean isActive() {
        if (cs == null) {
            return false;
        } else {
            return cs.isActive();
        }
    }

    private void createConnectorServer() throws IOException {
        // first create the registry
        createRegistry();
        
        // Retrieve the PlatformMBeanServer.
        final MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();

        // Environment map.
        HashMap<String,Object> env = new HashMap<String,Object>();
        
        final JMXServiceURL url = new JMXServiceURL(getServiceURL());

        // Now create the server from the JMXServiceURL
        cs = JMXConnectorServerFactory.newJMXConnectorServer(url, env, mbs);
    }
    
    private void createRegistry() throws IOException {
        // already created?
        if (registry != null) {
            return;
        }
        // Ensure cryptographically strong random number generator used
        // to choose the object number - see java.rmi.server.ObjID
        System.setProperty("java.rmi.server.randomIDs", "true");
        
        // set RMI hostname to host if property isn't set already
        // This fixes a hard to understand connection refused issue.
        String rmi_host = System.getProperty("java.rmi.server.hostname");
        if (rmi_host == null) {
            System.setProperty("java.rmi.server.hostname", host);
        }

        // Start or reuse an RMI registry on specified port
        try {
            registry = LocateRegistry.getRegistry(port);
            // provoke a RemoteException if registry doesn't exist yet.
            registry.list();
        }
        catch (Exception ignored) {
        	registry = LocateRegistry.createRegistry(port);
        }
        /*catch (IOException ex) {
            registry = LocateRegistry.createRegistry(port);
        }*/

    }

    /**
     * The CleanThread daemon thread will wait until all non-daemon threads
     * are terminated, excluding those non-daemon threads that are kept alive
     * by the presence of a started JMX RMI Connector Server. When no other
     * non-daemon threads remain, it stops the JMX RMI Connector Server,
     * allowing the application to terminate gracefully.
     */
    public static class CleanThread extends Thread {
        private JMXConnectorServer cs;

        public CleanThread() {
            super("JMX Agent Cleaner");
            this.cs = null;
            setDaemon(true);
        }
        
        protected void setCS(JMXConnectorServer cs) {
            this.cs = cs;
        }

        @Override
		public void run() {
            boolean loop = true;
            try {
                while (loop) {
                    final Thread[] all = new Thread[Thread.activeCount() + 100];
                    final int count = Thread.enumerate(all);
                    loop = false;
                    for (int i = 0; i < count; i++) {
                        final Thread t = all[i];
                        // daemon: skip it.
                        if (t.isDaemon()) continue;
                        // RMI Reaper: skip it.
                        if (t.getName().startsWith("RMI Reaper")) continue;
                        if (t.getName().startsWith("DestroyJavaVM")) continue;
                        // Non daemon, non RMI Reaper: join it, break the for
                        // loop, continue in the while loop (loop=true)
                        loop = true;
                        try {
                            // Found a non-daemon thread. Wait for it.
                            t.join();
                        }
                        catch (Exception ex) {
                            ex.printStackTrace();
                        }
                        break;
                    }
                }
                // We went through a whole for-loop without finding any thread
                // to join. We can close cs.
            }
            catch (Exception ex) {
                ex.printStackTrace();
            }
            finally {
                try {
                    // if we reach here it means the only non-daemon threads
                    // that remain are reaper threads - or that we got an
                    // unexpected exception/error.
                    //
                    if (cs != null && cs.isActive()) {
                        cs.stop();
                    }
                }
                catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        }
    }
}
