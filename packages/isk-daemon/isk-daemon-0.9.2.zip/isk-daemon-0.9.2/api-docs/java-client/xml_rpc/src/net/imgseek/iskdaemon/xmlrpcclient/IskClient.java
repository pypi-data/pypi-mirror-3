/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.iskdaemon.xmlrpcclient;

import static org.junit.Assert.assertEquals;

import java.net.MalformedURLException;
import java.net.URL;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.junit.Test;


/** Requires java XML-RPC client from http://ws.apache.org/xmlrpc/download.html
 * 
 * This test also requires the following image file (replace with anything else valid) 
 * c:\data\DSC00006.JPG
 * 
 * WARNING: running this test will remove all data on a database space with id 551 and 552 
 * 
 * 
 * @author rnc
 *
 */
public class IskClient {

	private static final long WAIT_TIME = 500;

	private static void log(String msg) {
		System.out.println(msg);
	}
	/**
	 * @param args
	 * @throws MalformedURLException 
	 * @throws XmlRpcException 
	 * @throws InterruptedException 
	 */
	public static void main(String[] args) throws MalformedURLException, XmlRpcException, InterruptedException {

	    XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
	    config.setServerURL(new URL("http://localhost:31128/RPC"));
	    XmlRpcClient client = new XmlRpcClient();
	    client.setConfig(config);
	    
	    log("Get all database spaces");
	    Object[] dbList = (Object[]) client.execute("getDbList", new Object[]{});
	    for (int i = 0; i < dbList.length; i++) {
	    	System.out.println((Integer)dbList[i]);			
		}
	    
	    log("Create db space 551");
	    assertEquals(551,
	    		client.execute("createDb", new Object[]{new Integer(551)}));
	    
	    log("Add images to database space 551");
	    assertEquals(1,client.execute("addImg", new Object[]{
	    		new Integer(551),
	    		new Integer(1),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		}));	    
	    client.execute("addImg", new Object[]{
	    		new Integer(551),
	    		new Integer(2),
	    		"c:\\data\\DSC00006.JPG"	    		
	    });	    
	    client.execute("addImg", new Object[]{
	    		new Integer(551),
	    		new Integer(3),
	    		"c:\\data\\DSC00006.JPG"	    		
	    });	    
	    client.execute("addImg", new Object[]{
	    		new Integer(551),
	    		new Integer(4),
	    		"c:\\data\\DSC00006.JPG"	    		
	    });	    
	    client.execute("addImg", new Object[]{
	    		new Integer(551),
	    		new Integer(5),
	    		"c:\\data\\DSC00006.JPG"	    		
	    });	    

	    Thread.sleep(WAIT_TIME);
	    
	    log("Get image count on db space 551");
	    Integer imgCount = (Integer) client.execute("getDbImgCount", new Object[]{new Integer(551)});
	    System.out.println(imgCount);
	    assertEquals(5, 
	    		imgCount);
	    
	    log("Query for similar images");
	    Object[] res =  (Object[])client.execute("queryImgID", new Object[]{new Integer(551),new Integer(2),new Integer(2)});
	    assert(res.length > 1);
	    for (int i = 0; i < res.length; i++) {
	    	Object[] resultPair = (Object[]) res[i];
	    	Integer imgId = (Integer)resultPair[0];
	    	Double imgRatio;
	    	try {
	    		imgRatio = (Double)resultPair[1];
	    	} catch (Exception e) {
	    		imgRatio = new Double((Integer)resultPair[1]);
			}
	    	System.out.println(imgId + " ("+ imgRatio+"%)");	    	
		}

	    log("Create db space 552");
	    assertEquals(552,
	    		client.execute("createDb", new Object[]{new Integer(552)}));
/*	    
	    log("Reset database 552");
	    assertEquals(1,
	    		client.execute("resetDb", new Object[]{new Integer(552)}));
*/	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Add image to database space 552");
	    assertEquals(1,client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(1),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		}));
	    log("Add image to database space 552");
	    assertEquals(1,client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(2),
	    		"c:\\data\\DSC00006.JPG"	    		
	    }));
	    log("Add image to database space 552");
	    assertEquals(1,client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(3),
	    		"c:\\data\\DSC00006.JPG"	    		
	    }));
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(3,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));

	    Thread.sleep(WAIT_TIME);
	    
	    log("Save all database spaces to data file defined on settings.py");
	    assert(((Integer)client.execute("saveAllDbs", new Object[]{}))>= 2);
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(3,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));

/*	    
	    log("Reset database 552");
	    assertEquals(1,
	    		client.execute("resetDb", new Object[]{new Integer(552)}));

*/	    
	    Thread.sleep(WAIT_TIME);

	    log("Database 552 image count");
	    assertEquals(3,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));

	    Thread.sleep(WAIT_TIME);

	    log("Add image to database space 552");
	    assertEquals(1,client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(5),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		}));
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(4,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));
	    
	    log("Load all database spaces from data file defined on settings.py");
	    assert((Integer)client.execute("loadAllDbs", new Object[]{}) >= 2);	    	    

	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(3,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Export a single database space to a data file: 552");
	    assertEquals(1,
	    		(Integer)client.execute("saveDbAs", new Object[]{new Integer(552), "c:\\db552.export"}));
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Add another image to database space 552");
	    client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(2),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		});
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(2,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));

	    Thread.sleep(WAIT_TIME);
	    
	    log("Save db space 552 again to a data file");
	    assertEquals(1,
	    		(Integer)client.execute("saveDb", new Object[]{new Integer(552)}));

	    Thread.sleep(WAIT_TIME);
	    
	    log("Add another image to database space 552");
	    client.execute("addImg", new Object[]{
	    		new Integer(552),
	    		new Integer(3),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		});

	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(3,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));

	    Thread.sleep(WAIT_TIME);
	    
	    log("Load db space 552 from a previously saved data file (can be considered a \"db space import\")");
	    assertEquals(552,
	    		(Integer)client.execute("loadDb", new Object[]{new Integer(552), "c:\\db552.export"}));
	    
	    Thread.sleep(WAIT_TIME);
	    
	    log("Database 552 image count");
	    assertEquals(2,
	    		(Integer)client.execute("getDbImgCount", new Object[]{new Integer(552)}));	    
	    
	    log("Calculate similarity between two images");
	    assert(((Double)client.execute("calcImgDiff", new Object[]{new Integer(552), new Integer(1),new Integer(2)})) < -20);	    

	}
	
	@Test	
	public void testAll() throws MalformedURLException, XmlRpcException, InterruptedException {
		main(null);
	}
}
